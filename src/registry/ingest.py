"""Context ingestion into the AST registry.

``ingest_context`` parses a source file (or directory tree) into an AST, computes
a structural *semantic hash*, extracts the functions/types it declares, stores
everything in the :class:`~src.registry.ast_db.ASTDatabase`, and registers the
context in ``blueprint.aero``'s ``[context_registry]`` so the blueprint stays the
single source of truth for which contexts are active.

Languages:

* **Python** is parsed with the stdlib :mod:`ast` module.  Comments are not part
  of the AST at all and whitespace never appears, so the structural hash is
  naturally insensitive to both.
* **Rust** is parsed with ``tree-sitter-rust``; comment nodes are filtered out of
  the structural walk so comment-only edits do not change the hash.

The semantic hash is a SHA-256 over the ordered tree of *node types* only — it
captures structure, not identifiers or literal values, exactly as intended for
detecting structurally-equivalent code across contexts.
"""

from __future__ import annotations

import ast as _py_ast
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.registry.ast_db import ASTDatabase, ASTEntry

# Extension -> language, and the reverse mapping used for directory walks.
_EXT_LANGUAGE = {
    ".py": "python",
    ".rs": "rust",
}
_LANGUAGE_EXTS = {
    "python": [".py"],
    "rust": [".rs"],
}

# tree-sitter node types that carry comments (filtered from the structural hash).
_RUST_COMMENT_NODES = {"line_comment", "block_comment"}


class IngestError(Exception):
    """Raised when a file cannot be parsed or the language is unsupported."""


@dataclass
class FileResult:
    path: str
    language: str
    semantic_hash: str
    functions: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)


@dataclass
class IngestResult:
    context_name: str
    files: List[FileResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    blueprint_updated: bool = False


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------
def detect_language(path: Path) -> Optional[str]:
    """Infer the language from a file extension, or ``None`` if unsupported."""
    return _EXT_LANGUAGE.get(path.suffix.lower())


# ---------------------------------------------------------------------------
# Python (stdlib ast)
# ---------------------------------------------------------------------------
def _python_structure(node: _py_ast.AST) -> Tuple[str, list]:
    """Build a (node_type, [children...]) structural tree, names/values dropped."""
    children = [_python_structure(c) for c in _py_ast.iter_child_nodes(node)]
    return (type(node).__name__, children)


def _parse_python(source: str) -> Dict[str, Any]:
    try:
        tree = _py_ast.parse(source)
    except SyntaxError as exc:  # pragma: no cover - exercised via tests
        raise IngestError(f"Python syntax error: {exc}") from exc

    functions: List[str] = []
    types: List[str] = []
    for node in _py_ast.walk(tree):
        if isinstance(node, (_py_ast.FunctionDef, _py_ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, _py_ast.ClassDef):
            types.append(node.name)

    structure = _python_structure(tree)
    return {
        "structure": structure,
        "functions": sorted(set(functions)),
        "types": sorted(set(types)),
    }


# ---------------------------------------------------------------------------
# Rust (tree-sitter)
# ---------------------------------------------------------------------------
def _rust_structure(node: Any) -> Optional[Tuple[str, list]]:
    if node.type in _RUST_COMMENT_NODES:
        return None
    children = []
    for child in node.named_children:
        sub = _rust_structure(child)
        if sub is not None:
            children.append(sub)
    return (node.type, children)


def _rust_node_name(node: Any, source: bytes) -> Optional[str]:
    name_node = node.child_by_field_name("name")
    if name_node is None:
        return None
    return source[name_node.start_byte:name_node.end_byte].decode("utf-8", "replace")


def _parse_rust(source: str) -> Dict[str, Any]:
    try:
        from translator.rust_ast import parse as _rs_parse
    except ImportError as exc:  # pragma: no cover - environment guard
        raise IngestError(
            "Rust ingestion requires 'tree-sitter' and 'tree-sitter-rust'. "
            "Install them with: pip install tree-sitter tree-sitter-rust"
        ) from exc

    encoded = source.encode("utf-8")
    tree = _rs_parse(source)
    root = tree.root_node

    functions: List[str] = []
    types: List[str] = []
    type_kinds = {"struct_item", "enum_item", "trait_item", "type_item", "union_item"}

    stack = [root]
    while stack:
        node = stack.pop()
        if node.type == "function_item":
            name = _rust_node_name(node, encoded)
            if name:
                functions.append(name)
        elif node.type in type_kinds:
            name = _rust_node_name(node, encoded)
            if name:
                types.append(name)
        stack.extend(node.named_children)

    structure = _rust_structure(root) or (root.type, [])
    return {
        "structure": structure,
        "functions": sorted(set(functions)),
        "types": sorted(set(types)),
    }


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------
def _hash_structure(structure: Any) -> str:
    """SHA-256 over a canonical JSON encoding of the structural node tree."""
    canonical = json.dumps(structure, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_source(source: str, language: str) -> Dict[str, Any]:
    """Parse *source* and return ``{structure, functions, types}`` for *language*."""
    if language == "python":
        return _parse_python(source)
    if language == "rust":
        return _parse_rust(source)
    raise IngestError(f"Unsupported language: {language!r}")


def semantic_hash(source: str, language: str) -> str:
    """Compute the structural semantic hash of *source* in *language*."""
    return _hash_structure(parse_source(source, language)["structure"])


# ---------------------------------------------------------------------------
# blueprint.aero [context_registry] update
# ---------------------------------------------------------------------------
def _toml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def update_context_registry(
    blueprint_path: Union[str, Path], name: str, path: str, language: str
) -> bool:
    """Register ``name`` under ``[context_registry]`` in the blueprint.

    Appends a ``[context_registry.<name>]`` sub-table when the context is not
    already present, preserving the rest of the file (and its comments).  Returns
    ``True`` if the blueprint was modified, ``False`` if the context already
    existed.
    """
    bp_path = Path(blueprint_path)
    existing_text = bp_path.read_text(encoding="utf-8") if bp_path.is_file() else ""

    # Detect whether the context is already registered.
    try:
        from src.blueprint import load_blueprint

        if bp_path.is_file() and name in load_blueprint(bp_path).context_registry:
            return False
    except Exception:
        # If the existing blueprint can't be parsed, fall through and append
        # anyway rather than silently dropping the registration.
        pass

    block_lines = [
        "",
        f"[context_registry.{name}]",
        f"path = {_toml_str(path)}",
        f"language = {_toml_str(language)}",
        "",
    ]
    new_text = existing_text
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"
    new_text += "\n".join(block_lines)

    bp_path.parent.mkdir(parents=True, exist_ok=True)
    bp_path.write_text(new_text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def _iter_source_files(root: Path, language: Optional[str]) -> List[Path]:
    if root.is_file():
        return [root]
    exts = _LANGUAGE_EXTS.get(language) if language else None
    files: List[Path] = []
    for candidate in sorted(root.rglob("*")):
        if not candidate.is_file():
            continue
        if exts is not None:
            if candidate.suffix.lower() in exts:
                files.append(candidate)
        elif candidate.suffix.lower() in _EXT_LANGUAGE:
            files.append(candidate)
    return files


def ingest_context(
    context_name: str,
    path: Union[str, Path],
    language: Optional[str] = None,
    *,
    db: Optional[ASTDatabase] = None,
    db_path: Optional[Union[str, Path]] = None,
    blueprint_path: Optional[Union[str, Path]] = None,
) -> IngestResult:
    """Ingest a file or directory tree into the registry under *context_name*.

    Parses each source file, computes its semantic hash, stores the AST/metadata
    in the registry DB, and registers the context in ``blueprint.aero``.

    Either ``db`` (an open :class:`ASTDatabase`) or ``db_path`` must resolve to a
    database; if neither is given, a default ``.aero/registry.db`` next to the
    target path is used.
    """
    target = Path(path)
    if not target.exists():
        raise IngestError(f"Path does not exist: {target}")

    owns_db = False
    if db is None:
        if db_path is None:
            base = target if target.is_dir() else target.parent
            db_path = base / ".aero" / "registry.db"
        db = ASTDatabase(db_path)
        owns_db = True

    result = IngestResult(context_name=context_name)
    try:
        files = _iter_source_files(target, language)
        if not files:
            result.errors.append(f"No supported source files found under {target}")

        for file_path in files:
            file_language = language or detect_language(file_path)
            if file_language is None:
                result.errors.append(f"Unsupported file type: {file_path}")
                continue
            try:
                source = file_path.read_text(encoding="utf-8")
                parsed = parse_source(source, file_language)
            except (IngestError, OSError, UnicodeDecodeError) as exc:
                result.errors.append(f"{file_path}: {exc}")
                continue

            digest = _hash_structure(parsed["structure"])
            entry = ASTEntry(
                context_name=context_name,
                semantic_hash=digest,
                language=file_language,
                path=str(file_path),
                ast=parsed["structure"],
                functions=parsed["functions"],
                types=parsed["types"],
            )
            db.upsert(entry)
            result.files.append(
                FileResult(
                    path=str(file_path),
                    language=file_language,
                    semantic_hash=digest,
                    functions=parsed["functions"],
                    types=parsed["types"],
                )
            )

        # Register the context in the blueprint (path + dominant language).
        if blueprint_path is not None and result.files:
            registry_language = language or result.files[0].language
            result.blueprint_updated = update_context_registry(
                blueprint_path, context_name, str(target), registry_language
            )
    finally:
        if owns_db:
            db.close()

    return result
