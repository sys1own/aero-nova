import hashlib
import importlib
import time
import warnings
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

MAX_FILE_BYTES = 1_000_000
PARSE_TIMEOUT_SECONDS = 5.0

LANGUAGE_BY_EXTENSION: Dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".rs": "rust",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp", ".hxx": "cpp",
    ".c": "c", ".h": "c",
    ".f": "fortran", ".f90": "fortran", ".f95": "fortran", 
    ".f03": "fortran", ".for": "fortran",
    ".cob": "cobol", ".cbl": "cobol", ".cpy": "cobol",
}

GRAMMAR_MODULES: Dict[str, str] = {
    "python": "tree_sitter_python",
    "rust": "tree_sitter_rust",
    "cpp": "tree_sitter_cpp",
    "c": "tree_sitter_c",
    "fortran": "tree_sitter_fortran",
    "cobol": "tree_sitter_cobol",
}

_LANGUAGE_CACHE: Dict[str, Any] = {}

class UniversalParseError(Exception):
    """Raised when no grammar can be resolved/loaded for a language."""

def supported_extensions() -> List[str]:
    return sorted(LANGUAGE_BY_EXTENSION)

def supported_languages() -> List[str]:
    return sorted(set(LANGUAGE_BY_EXTENSION.values()))

def detect_language(path: Union[str, Path]) -> Optional[str]:
    return LANGUAGE_BY_EXTENSION.get(Path(path).suffix.lower())

def _load_language(language: str):
    if language in _LANGUAGE_CACHE:
        return _LANGUAGE_CACHE[language]

    module_name = GRAMMAR_MODULES.get(language)
    if module_name is None:
        raise UniversalParseError(f"No grammar module registered for language {language!r}")

    try:
        grammar = importlib.import_module(module_name)
        from tree_sitter import Language as TSLanguage
        lang_obj = TSLanguage(grammar.language(), language)
    except Exception as exc:
        raise UniversalParseError(f"No valid grammar could be resolved for language {language!r}") from exc

    _LANGUAGE_CACHE[language] = lang_obj
    return lang_obj

def _build_parser(language: str):
    from tree_sitter import Parser
    return Parser(_load_language(language))


class NodeCategory(str, Enum):
    DECLARATION = "DECLARATION"
    STATEMENT = "STATEMENT"
    EXPRESSION = "EXPRESSION"
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    TYPE = "TYPE"
    KEYWORD = "KEYWORD"
    COMMENT = "COMMENT"
    PUNCTUATION = "PUNCTUATION"
    MODULE = "MODULE"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


# Cross-language alignment: language-specific node type -> uniform canonical kind.
CANONICAL_KIND: Dict[str, Dict[str, str]] = {
    "python": {
        "function_definition": "function_declaration",
        "class_definition": "type_declaration",
        "import_statement": "import_declaration",
        "import_from_statement": "import_declaration",
        "module": "translation_unit",
    },
    "rust": {
        "function_item": "function_declaration",
        "struct_item": "type_declaration",
        "enum_item": "type_declaration",
        "union_item": "type_declaration",
        "trait_item": "type_declaration",
        "type_item": "type_declaration",
        "use_declaration": "import_declaration",
        "mod_item": "module_declaration",
        "source_file": "translation_unit",
    },
    "cpp": {
        "function_definition": "function_declaration",
        "class_specifier": "type_declaration",
        "struct_specifier": "type_declaration",
        "namespace_definition": "module_declaration",
        "preproc_include": "import_declaration",
        "translation_unit": "translation_unit",
    },
    "c": {
        "function_definition": "function_declaration",
        "struct_specifier": "type_declaration",
        "union_specifier": "type_declaration",
        "preproc_include": "import_declaration",
        "translation_unit": "translation_unit",
    },
    "fortran": {
        "function": "function_declaration",
        "subroutine": "function_declaration",
        "module": "module_declaration",
        "derived_type_definition": "type_declaration",
        "translation_unit": "translation_unit",
    },
    "cobol": {
        # Best-effort; COBOL grammars vary in node naming.
        "method_definition": "function_declaration",
        "paragraph": "function_declaration",
        "program_definition": "module_declaration",
    },
}

# Node types that represent comments, across grammars.
_COMMENT_TYPES = {"comment", "line_comment", "block_comment", "doc_comment"}

# Explicit per-category type hints shared by most C-family / curly grammars.
_DECLARATION_SUFFIXES = ("_definition", "_declaration", "_item", "_specifier", "_declarator")
_STATEMENT_SUFFIXES = ("_statement",)
_EXPRESSION_SUFFIXES = ("_expression", "_expr")
_LITERAL_HINTS = ("literal", "number", "string", "char", "integer", "float", "boolean", "true", "false")
_IDENTIFIER_HINTS = ("identifier",)
_TYPE_HINTS = ("type_identifier", "primitive_type", "type")


def _categorize(language: str, node_type: str, named: bool, is_error: bool, is_missing: bool) -> NodeCategory:
    if is_error or is_missing or node_type == "ERROR":
        return NodeCategory.ERROR
    if node_type in _COMMENT_TYPES:
        return NodeCategory.COMMENT

    canonical = CANONICAL_KIND.get(language, {}).get(node_type)
    if canonical:
        if canonical.endswith("_declaration"):
            return NodeCategory.DECLARATION
        if canonical.endswith("translation_unit"):
            return NodeCategory.MODULE

    if not named:
        # Anonymous tokens are keywords or punctuation.
        return NodeCategory.KEYWORD if node_type.isalpha() else NodeCategory.PUNCTUATION

    lowered = node_type.lower()
    if any(lowered.endswith(s) for s in _DECLARATION_SUFFIXES):
        return NodeCategory.DECLARATION
    if any(lowered.endswith(s) for s in _STATEMENT_SUFFIXES):
        return NodeCategory.STATEMENT
    if any(lowered.endswith(s) for s in _EXPRESSION_SUFFIXES):
        return NodeCategory.EXPRESSION
    if lowered in _TYPE_HINTS:
        return NodeCategory.TYPE
    if any(h in lowered for h in _IDENTIFIER_HINTS):
        return NodeCategory.IDENTIFIER
    if any(h in lowered for h in _LITERAL_HINTS):
        return NodeCategory.LITERAL
    return NodeCategory.UNKNOWN


def _canonical_kind(language: str, node_type: str) -> Optional[str]:
    return CANONICAL_KIND.get(language, {}).get(node_type)


# ---------------------------------------------------------------------------
# 2. Lossless CST -> 3. Flat UAST (the Psi transform)
# ---------------------------------------------------------------------------
def _flatten(root, language: str, source: bytes) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Linearise the CST into a 1-D node array with parent/children pointers."""
    nodes: List[Dict[str, Any]] = []
    counts = {"error": 0, "missing": 0}

    # Pre-order DFS so id 0 is the root.
    stack: List[Tuple[Any, Optional[int]]] = [(root, None)]
    # We need children IDs after assigning ids; do a two-pass via recursion-like
    # explicit traversal that records children as it goes.
    def visit(node, parent_id: Optional[int]) -> int:
        node_id = len(nodes)
        is_error = bool(node.is_error) or node.type == "ERROR"
        is_missing = bool(node.is_missing)
        if is_error:
            counts["error"] += 1
        if is_missing:
            counts["missing"] += 1

        category = _categorize(language, node.type, node.is_named, is_error, is_missing)
        record: Dict[str, Any] = {
            "id": node_id,
            "parent": parent_id,
            "children": [],
            "type": node.type,
            "grammar": getattr(node, "grammar_name", node.type),
            "category": category.value,
            "canonical_kind": _canonical_kind(language, node.type),
            "named": bool(node.is_named),
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "start_point": [node.start_point[0], node.start_point[1]],
            "end_point": [node.end_point[0], node.end_point[1]],
            "is_error": is_error,
            "is_missing": is_missing,
        }
        if is_error or is_missing:
            # Symbolic placeholder: keep offsets, mark a uniform kind.
            record["canonical_kind"] = "missing_placeholder" if is_missing else "error_placeholder"
        nodes.append(record)

        for child in node.children:
            child_id = visit(child, node_id)
            record["children"].append(child_id)

        # Leaf tokens carry their literal text so the CST is reconstructable.
        if not node.children:
            record["text"] = source[node.start_byte:node.end_byte].decode("utf-8", "replace")
        return node_id

    visit(root, None)
    return nodes, counts


# ---------------------------------------------------------------------------
# 4. Deterministic semantic hashing
# ---------------------------------------------------------------------------
_NON_STRUCTURAL = {NodeCategory.COMMENT.value, NodeCategory.PUNCTUATION.value}


def semantic_hash_from_nodes(nodes: List[Dict[str, Any]]) -> str:
    """SHA-256 over structural constructs only (comments/whitespace filtered)."""
    tokens: List[str] = []
    for node in nodes:
        if node["category"] in _NON_STRUCTURAL:
            continue
        if not node["named"]:
            continue  # anonymous punctuation/keywords are not structural nodes
        tokens.append(node.get("canonical_kind") or node["type"])
    digest = hashlib.sha256("\n".join(tokens).encode("utf-8"))
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Symbol extraction (functions / types) via canonical alignment
# ---------------------------------------------------------------------------
def _node_name(node_id: int, nodes: List[Dict[str, Any]], source_text: str) -> Optional[str]:
    """Best-effort name of a declaration node: first identifier-ish descendant."""
    node = nodes[node_id]
    # Breadth-first over descendants, preferring shallow identifiers.
    queue = list(node["children"])
    while queue:
        cid = queue.pop(0)
        child = nodes[cid]
        ctype = child["type"]
        if ctype in ("identifier", "type_identifier", "name", "field_identifier"):
            text = child.get("text")
            if text is None:
                text = source_text[child["start_byte"]:child["end_byte"]]
            return text
        queue.extend(child["children"])
    return None


def extract_symbols(uast: Dict[str, Any], source: str = "") -> Dict[str, List[str]]:
    """Pull declared function/type names out of a UAST using canonical kinds."""
    nodes = uast["nodes"]
    functions: List[str] = []
    types: List[str] = []
    for node in nodes:
        kind = node.get("canonical_kind")
        if kind == "function_declaration":
            name = _node_name(node["id"], nodes, source)
            if name:
                functions.append(name)
        elif kind == "type_declaration":
            name = _node_name(node["id"], nodes, source)
            if name:
                types.append(name)
    return {"functions": sorted(set(functions)), "types": sorted(set(types))}


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------
def _empty_uast(language: str, source: bytes, file_path: Optional[str], flags: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "metadata": {
            "language": language,
            "file_path": file_path,
            "file_hash": hashlib.sha256(source).hexdigest(),
            "source_bytes": len(source),
            "byte_span": [0, len(source)],
            "node_count": 0,
            "parser_flags": flags,
        },
        "root": None,
        "nodes": [],
        "semantic_hash": hashlib.sha256(b"").hexdigest(),
    }


def parse_bytes(
    source: bytes,
    language: str,
    *,
    file_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse raw *source* bytes in *language* into a UAST dict.

    Files over :data:`MAX_FILE_BYTES` or parses exceeding
    :data:`PARSE_TIMEOUT_SECONDS` are bypassed and flagged.
    """
    base_flags: Dict[str, Any] = {
        "fallback": False,
        "fallback_reason": None,
        "has_error": False,
        "error_nodes": 0,
        "missing_nodes": 0,
        "error_locations": [],
        "truncated": False,
        "parse_seconds": 0.0,
    }

    if len(source) > MAX_FILE_BYTES:
        flags = dict(base_flags, fallback=True, fallback_reason="file_too_large", truncated=True)
        return _empty_uast(language, source, file_path, flags)

    parser = _build_parser(language)

    # Primary timeout mechanism: Tree-sitter's own budget (microseconds).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            parser.timeout_micros = int(PARSE_TIMEOUT_SECONDS * 1_000_000)
        except Exception:  # pragma: no cover - older/newer bindings
            pass

    start = time.monotonic()
    try:
        tree = parser.parse(source)
    except Exception as exc:  # pragma: no cover - parser-level failure
        flags = dict(base_flags, fallback=True, fallback_reason=f"parse_exception:{exc}")
        return _empty_uast(language, source, file_path, flags)
    elapsed = time.monotonic() - start

    if tree is None or elapsed > PARSE_TIMEOUT_SECONDS:
        flags = dict(
            base_flags,
            fallback=True,
            fallback_reason="parse_timeout",
            truncated=True,
            parse_seconds=round(elapsed, 4),
        )
        return _empty_uast(language, source, file_path, flags)

    nodes, counts = _flatten(tree.root_node, language, source)

    error_locations = [
        {
            "node_id": n["id"],
            "kind": "missing" if n["is_missing"] else "error",
            "start_byte": n["start_byte"],
            "end_byte": n["end_byte"],
            "start_point": n["start_point"],
        }
        for n in nodes
        if n["is_error"] or n["is_missing"]
    ]

    flags = dict(
        base_flags,
        has_error=bool(tree.root_node.has_error),
        error_nodes=counts["error"],
        missing_nodes=counts["missing"],
        error_locations=error_locations,
        parse_seconds=round(elapsed, 4),
    )

    uast: Dict[str, Any] = {
        "metadata": {
            "language": language,
            "file_path": file_path,
            "file_hash": hashlib.sha256(source).hexdigest(),
            "source_bytes": len(source),
            "byte_span": [tree.root_node.start_byte, tree.root_node.end_byte],
            "node_count": len(nodes),
            "parser_flags": flags,
        },
        "root": 0 if nodes else None,
        "nodes": nodes,
    }
    uast["semantic_hash"] = semantic_hash_from_nodes(nodes)
    return uast


def parse_source(source: str, language: str, *, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Parse *source* text in *language* into a UAST dict."""
    return parse_bytes(source.encode("utf-8"), language, file_path=file_path)


def parse_file(path: Union[str, Path], language: Optional[str] = None) -> Dict[str, Any]:
    """Parse a file into a UAST dict, resolving the grammar from its extension."""
    file_path = Path(path)
    resolved = language or detect_language(file_path)
    if resolved is None:
        raise UniversalParseError(f"Unsupported file extension: {file_path.suffix!r}")
    data = file_path.read_bytes()
    return parse_bytes(data, resolved, file_path=str(file_path))


def semantic_hash(source: str, language: str) -> str:
    """Compute the deterministic structural semantic hash of *source*."""
    return parse_source(source, language)["semantic_hash"]