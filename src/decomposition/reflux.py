"""Self-healing dependency reflux & utility consolidation engine.

After the splitter produces decomposed leaf modules, two systemic issues
can arise:

1. **Duplicate shared utilities** — helper functions copied verbatim into
   every leaf module instead of being shared.
2. **Missing cross-module imports** — a leaf module calls a symbol defined
   in a sibling module without importing it, causing ``NameError`` at
   runtime.

This module implements two post-processing passes that run on the
``decomposed/<pkg>/`` directory tree *immediately* after splitting:

- **Pass 1 (``consolidate_shared_utils``):** detects duplicate function
  definitions across leaf modules, extracts them into a single
  ``utils.py``, and removes the originals from the leaves.
- **Pass 2 (``inject_missing_imports``):** scans each leaf for names used
  but not defined or imported, then injects the correct relative import
  from either ``utils.py`` or a sibling module.

A final ``scan_anomalies`` validation pass confirms zero unresolved
symbols remain.
"""

from __future__ import annotations

import ast
import collections
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class RefluxResult:
    """Summary returned by :func:`run_reflux`."""

    utils_created: bool = False
    utils_path: Optional[str] = None
    utils_bytes: int = 0
    functions_consolidated: int = 0
    imports_injected: int = 0
    files_patched: List[str] = field(default_factory=list)
    anomalies_remaining: int = 0
    errors: List[str] = field(default_factory=list)
    extra_files: List[str] = field(default_factory=list)
    extra_bytes: int = 0


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _parse_file(path: Path) -> Optional[ast.Module]:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


def _defined_names(tree: ast.Module) -> Dict[str, ast.stmt]:
    """Return top-level names defined in *tree* mapped to their AST node."""
    defs: Dict[str, ast.stmt] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs[node.name] = node
        elif isinstance(node, ast.ClassDef):
            defs[node.name] = node
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defs[target.id] = node
    return defs


def _imported_names(tree: ast.Module) -> Set[str]:
    """Return names explicitly imported at the top level."""
    names: Set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def _used_names(tree: ast.Module) -> Set[str]:
    """Return all ``ast.Name`` identifiers loaded anywhere in *tree*."""
    names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            names.add(node.id)
    return names


def _function_source(path: Path, node: ast.stmt) -> str:
    """Extract source text for a top-level function/class node."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = node.lineno - 1
    end = node.end_lineno if node.end_lineno else start + 1
    return "".join(lines[start:end])


def _normalize_body(source: str) -> str:
    """Normalize whitespace for duplicate comparison."""
    return "\n".join(line.rstrip() for line in source.strip().splitlines())


# ---------------------------------------------------------------------------
# Pass 1: Shared Code Consolidation
# ---------------------------------------------------------------------------

def consolidate_shared_utils(pkg_dir: Path) -> Tuple[RefluxResult, Dict[str, str]]:
    """Detect duplicate functions across leaf modules and extract to utils.py.

    Returns the partial ``RefluxResult`` and a mapping of
    ``{function_name: module_stem}`` for every symbol now in utils.py,
    so Pass 2 can resolve references to them.
    """
    result = RefluxResult()
    # symbol_name -> [(file_path, normalized_source, ast_node)]
    func_registry: Dict[str, List[Tuple[Path, str, ast.stmt]]] = collections.defaultdict(list)

    leaf_files = sorted(
        p for p in pkg_dir.iterdir()
        if p.suffix == ".py" and p.name not in ("__init__.py", "utils.py")
    )

    for fpath in leaf_files:
        tree = _parse_file(fpath)
        if tree is None:
            continue
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                src = _function_source(fpath, node)
                normed = _normalize_body(src)
                func_registry[node.name].append((fpath, normed, node))

    # Find duplicates: functions with identical normalised bodies in ≥2 files
    duplicates: Dict[str, str] = {}  # name -> canonical source
    for name, occurrences in func_registry.items():
        if len(occurrences) < 2:
            continue
        # Group by body text
        body_groups: Dict[str, List[Path]] = collections.defaultdict(list)
        for fpath, normed, _node in occurrences:
            body_groups[normed].append(fpath)
        for body, files in body_groups.items():
            if len(files) >= 2:
                # Pick the first occurrence's raw source as canonical
                for fpath, normed, node in occurrences:
                    if normed == body:
                        duplicates[name] = _function_source(fpath, node)
                        break

    if not duplicates:
        return result, {}

    # Build utils.py content
    utils_lines = ['"""Shared utilities consolidated by the AeroNova reflux engine."""\n']

    # Collect all import blocks from leaf files that define these functions,
    # to include necessary imports in utils.py
    all_import_lines: Set[str] = set()
    for fpath in leaf_files:
        tree = _parse_file(fpath)
        if tree is None:
            continue
        source_lines = fpath.read_text(encoding="utf-8").splitlines(keepends=True)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                start = node.lineno - 1
                end = node.end_lineno if node.end_lineno else start + 1
                imp_text = "".join(source_lines[start:end]).rstrip()
                # Skip relative imports from the same package
                if isinstance(node, ast.ImportFrom) and node.level and node.level > 0:
                    continue
                all_import_lines.add(imp_text)

    for imp in sorted(all_import_lines):
        utils_lines.append(imp)
    utils_lines.append("")
    utils_lines.append("")

    for name, source in sorted(duplicates.items()):
        utils_lines.append(source.rstrip())
        utils_lines.append("")
        utils_lines.append("")

    utils_content = "\n".join(utils_lines)
    utils_path = pkg_dir / "utils.py"
    utils_path.write_text(utils_content, encoding="utf-8")
    utils_bytes = len(utils_content.encode("utf-8"))

    result.utils_created = True
    result.utils_path = str(utils_path)
    result.utils_bytes = utils_bytes
    result.functions_consolidated = len(duplicates)
    result.extra_files.append(str(utils_path))
    result.extra_bytes += utils_bytes

    # Remove duplicate definitions from leaf modules and add import from .utils
    for fpath in leaf_files:
        tree = _parse_file(fpath)
        if tree is None:
            continue
        source = fpath.read_text(encoding="utf-8")
        source_lines = source.splitlines(keepends=True)
        modified = False
        # Work backwards to preserve line numbers
        removals: List[Tuple[int, int]] = []
        names_to_import: List[str] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in duplicates:
                    raw = _function_source(fpath, node)
                    normed = _normalize_body(raw)
                    if normed == _normalize_body(duplicates[node.name]):
                        start = node.lineno - 1
                        end = node.end_lineno if node.end_lineno else start + 1
                        removals.append((start, end))
                        names_to_import.append(node.name)
                        modified = True

        if not modified:
            continue

        # Remove lines in reverse order
        for start, end in sorted(removals, reverse=True):
            del source_lines[start:end]

        # Add import statement for consolidated functions
        import_line = "from .utils import " + ", ".join(sorted(names_to_import)) + "\n"

        # Insert after existing imports
        insert_pos = 0
        for i, line in enumerate(source_lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "#", '"""', "'''")):
                insert_pos = i + 1
            elif stripped == "":
                if insert_pos > 0:
                    insert_pos = i + 1
            else:
                break

        source_lines.insert(insert_pos, import_line)

        new_content = "".join(source_lines)
        fpath.write_text(new_content, encoding="utf-8")
        result.files_patched.append(str(fpath))

    # Update __init__.py to include utils
    init_path = pkg_dir / "__init__.py"
    if init_path.exists():
        init_content = init_path.read_text(encoding="utf-8")
        if "from .utils import" not in init_content:
            # Add utils imports
            utils_exports = ", ".join(sorted(duplicates.keys()))
            new_line = f"from .utils import {utils_exports}\n"
            init_content = init_content.rstrip() + "\n" + new_line
            init_path.write_text(init_content, encoding="utf-8")

    utils_symbols = {name: "utils" for name in duplicates}
    return result, utils_symbols


# ---------------------------------------------------------------------------
# Pass 2: Self-Healing Import Reflux
# ---------------------------------------------------------------------------

def inject_missing_imports(
    pkg_dir: Path,
    utils_symbols: Dict[str, str],
) -> Tuple[int, List[str]]:
    """For every leaf module, find used-but-undefined names and inject imports.

    Parameters
    ----------
    pkg_dir : Path
        The decomposed package directory.
    utils_symbols : dict
        ``{name: "utils"}`` for symbols consolidated into ``utils.py``.

    Returns
    -------
    (imports_injected, files_patched)
    """
    # Build a global symbol index: name -> module_stem
    symbol_index: Dict[str, str] = dict(utils_symbols)

    leaf_files = sorted(
        p for p in pkg_dir.iterdir()
        if p.suffix == ".py" and p.name != "__init__.py"
    )

    # Index all top-level definitions across all sibling modules
    for fpath in leaf_files:
        tree = _parse_file(fpath)
        if tree is None:
            continue
        for name in _defined_names(tree):
            # Don't overwrite utils entries; sibling is fallback
            if name not in symbol_index:
                symbol_index[name] = fpath.stem

    # Python builtins to ignore
    builtins_set = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))

    total_injected = 0
    files_patched: List[str] = []

    for fpath in leaf_files:
        tree = _parse_file(fpath)
        if tree is None:
            continue

        defined = set(_defined_names(tree).keys())
        imported = _imported_names(tree)
        used = _used_names(tree)

        # Names that are used but neither defined nor imported nor builtin
        missing = used - defined - imported - builtins_set - {
            "self", "cls", "True", "False", "None",
            "__name__", "__file__", "__doc__", "__all__",
        }

        if not missing:
            continue

        # Resolve each missing name
        new_imports: Dict[str, List[str]] = collections.defaultdict(list)  # module -> [names]
        for name in sorted(missing):
            if name in symbol_index:
                source_module = symbol_index[name]
                if source_module != fpath.stem:  # Don't import from self
                    new_imports[source_module].append(name)

        if not new_imports:
            continue

        source = fpath.read_text(encoding="utf-8")
        source_lines = source.splitlines(keepends=True)

        # Find insertion point: after existing imports
        insert_pos = 0
        for i, line in enumerate(source_lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "#", '"""', "'''")):
                insert_pos = i + 1
            elif stripped == "":
                if insert_pos > 0:
                    insert_pos = i + 1
            else:
                break

        # Build import lines
        import_additions: List[str] = []
        for module, names in sorted(new_imports.items()):
            imp_line = f"from .{module} import {', '.join(sorted(names))}\n"
            # Don't add if already present
            if imp_line not in source:
                import_additions.append(imp_line)
                total_injected += len(names)

        if not import_additions:
            continue

        for imp_line in reversed(import_additions):
            source_lines.insert(insert_pos, imp_line)

        new_content = "".join(source_lines)
        fpath.write_text(new_content, encoding="utf-8")
        files_patched.append(str(fpath))

    return total_injected, files_patched


# ---------------------------------------------------------------------------
# Validation: Anomaly Scanner
# ---------------------------------------------------------------------------

def scan_anomalies(pkg_dir: Path) -> List[str]:
    """Scan all leaf modules for unresolved symbol references.

    Returns a list of ``"<file>: <name>"`` strings for every name that is
    used but neither defined, imported, nor a Python builtin.
    """
    builtins_set = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))
    ignore = builtins_set | {
        "self", "cls", "True", "False", "None",
        "__name__", "__file__", "__doc__", "__all__",
    }

    # Build index of all symbols available in the package
    pkg_symbols: Set[str] = set()
    leaf_files = sorted(
        p for p in pkg_dir.iterdir()
        if p.suffix == ".py"
    )
    for fpath in leaf_files:
        tree = _parse_file(fpath)
        if tree is None:
            continue
        pkg_symbols.update(_defined_names(tree).keys())

    anomalies: List[str] = []
    for fpath in leaf_files:
        if fpath.name == "__init__.py":
            continue
        tree = _parse_file(fpath)
        if tree is None:
            continue

        defined = set(_defined_names(tree).keys())
        imported = _imported_names(tree)
        used = _used_names(tree)

        missing = used - defined - imported - ignore

        # Filter: only flag names that exist somewhere in the package
        # (truly external unknowns are not our concern)
        for name in sorted(missing):
            if name in pkg_symbols:
                anomalies.append(f"{fpath.name}: {name}")

    return anomalies


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_reflux(pkg_dir: Path) -> RefluxResult:
    """Execute the full two-pass reflux pipeline on a decomposed package.

    Parameters
    ----------
    pkg_dir : Path
        Directory containing the decomposed leaf modules, ``__init__.py``,
        etc.  Typically ``build_artifacts/decomposed/<stem>/``.

    Returns
    -------
    RefluxResult
        Summary of consolidation, injection, and anomaly scan.
    """
    if not pkg_dir.is_dir():
        r = RefluxResult()
        r.errors.append(f"Package directory not found: {pkg_dir}")
        return r

    # Pass 1: consolidate duplicates into utils.py
    result, utils_symbols = consolidate_shared_utils(pkg_dir)

    # Pass 2: inject missing imports
    injected, patched = inject_missing_imports(pkg_dir, utils_symbols)
    result.imports_injected = injected
    result.files_patched = list(set(result.files_patched) | set(patched))

    # Validation: scan for remaining anomalies
    anomalies = scan_anomalies(pkg_dir)
    result.anomalies_remaining = len(anomalies)
    if anomalies:
        result.errors.extend(f"unresolved: {a}" for a in anomalies)

    return result
