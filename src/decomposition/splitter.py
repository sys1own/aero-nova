"""Physical file-splitting engine for polyglot decomposition.

When the FSM selects ``execute_polyglot_decomposition`` or
``boost_mutation_sigma`` under AGGRESSIVE_MUTATION, this module reads the
source files mapped in the context registry, parses them for top-level
structural boundaries (classes, large functions), and physically writes
them out as decoupled modules inside the target sandbox directory.

An ``__init__.py`` is generated to link the new modules together.
"""

from __future__ import annotations

import ast
import os
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SplitResult:
    """Result of a decomposition run."""

    files_written: List[str] = field(default_factory=list)
    bytes_written: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class _ExtractedUnit:
    """A single top-level unit extracted from a monolith."""

    name: str
    kind: str  # "class" or "function"
    source: str
    imports: str  # import statements needed by this unit


def _collect_imports(tree: ast.Module) -> str:
    """Extract all top-level import statements from the AST."""
    import_lines: List[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_lines.append(ast.get_source_segment("", node) or "")
    return ""


def _extract_import_block(source: str) -> str:
    """Extract the leading import block from source text."""
    lines = source.splitlines(keepends=True)
    import_lines: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            import_lines.append(line)
        elif stripped.startswith("#") or stripped == "" or stripped.startswith('"""') or stripped.startswith("'''"):
            import_lines.append(line)
        else:
            # Stop at first non-import, non-comment, non-blank line
            # unless we haven't found any imports yet
            if import_lines:
                break
    return "".join(import_lines)


def _extract_units(source: str, min_lines: int = 5) -> List[_ExtractedUnit]:
    """Parse source and extract top-level classes and large functions."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    lines = source.splitlines(keepends=True)
    import_block = _extract_import_block(source)
    units: List[_ExtractedUnit] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            start = node.lineno - 1
            end = node.end_lineno if node.end_lineno else start + 1
            body = "".join(lines[start:end])
            if (end - start) >= min_lines:
                units.append(_ExtractedUnit(
                    name=node.name,
                    kind="class",
                    source=body,
                    imports=import_block,
                ))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno - 1
            end = node.end_lineno if node.end_lineno else start + 1
            body = "".join(lines[start:end])
            if (end - start) >= min_lines:
                units.append(_ExtractedUnit(
                    name=node.name,
                    kind="function",
                    source=body,
                    imports=import_block,
                ))

    return units


def _write_module(
    output_dir: Path, unit: _ExtractedUnit, original_stem: str
) -> tuple:
    """Write a single extracted unit as a module file. Returns (path, bytes)."""
    # Normalize module filename
    module_name = f"{original_stem}_{unit.name.lower()}"
    file_path = output_dir / f"{module_name}.py"

    header = f'"""Auto-decomposed from monolith: {unit.kind} {unit.name}."""\n\n'
    content = header + unit.imports + "\n\n" + unit.source + "\n"

    file_path.write_text(content, encoding="utf-8")
    return str(file_path), len(content.encode("utf-8"))


def _generate_init(
    output_dir: Path, units: List[_ExtractedUnit], original_stem: str
) -> tuple:
    """Generate __init__.py that re-exports all split modules."""
    init_path = output_dir / "__init__.py"
    lines = [
        f'"""Auto-generated module index for decomposed {original_stem}."""\n',
    ]
    for unit in units:
        module_name = f"{original_stem}_{unit.name.lower()}"
        if unit.kind == "class":
            lines.append(f"from .{module_name} import {unit.name}")
        else:
            lines.append(f"from .{module_name} import {unit.name}")
    lines.append("")  # trailing newline
    content = "\n".join(lines)
    init_path.write_text(content, encoding="utf-8")
    return str(init_path), len(content.encode("utf-8"))


def decompose_source(
    source_path: Path,
    output_dir: Path,
    *,
    min_lines: int = 5,
) -> SplitResult:
    """Decompose a single Python source file into modular units.

    Parameters
    ----------
    source_path : Path
        Absolute path to the monolith source file.
    output_dir : Path
        Directory where split modules will be written.
    min_lines : int
        Minimum line count for a unit to be extracted (avoids trivial splits).

    Returns
    -------
    SplitResult
        Summary of files written and bytes produced.
    """
    result = SplitResult()

    if not source_path.exists() or not source_path.is_file():
        result.errors.append(f"Source not found: {source_path}")
        return result

    try:
        source = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        result.errors.append(f"Cannot read {source_path}: {exc}")
        return result

    units = _extract_units(source, min_lines=min_lines)
    if not units:
        result.errors.append(f"No extractable units in {source_path}")
        return result

    original_stem = source_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    for unit in units:
        try:
            path, nbytes = _write_module(output_dir, unit, original_stem)
            result.files_written.append(path)
            result.bytes_written += nbytes
        except OSError as exc:
            result.errors.append(f"Write failed for {unit.name}: {exc}")

    # Generate __init__.py
    try:
        path, nbytes = _generate_init(output_dir, units, original_stem)
        result.files_written.append(path)
        result.bytes_written += nbytes
    except OSError as exc:
        result.errors.append(f"__init__.py generation failed: {exc}")

    return result


def run_decomposition(
    metadata: Dict[str, Any],
    workspace: Path,
) -> Dict[str, Any]:
    """Entry point called by the orchestrator when decomposition is triggered.

    Reads context_registry entries from metadata, decomposes each source file,
    and returns a summary dict with ``decomposition_files_written`` and
    ``decomposition_bytes_written`` to be merged into the build metadata.
    """
    registry = metadata.get("context_registry")
    blueprint_dir = metadata.get("blueprint_dir", str(workspace))
    output_dir = workspace / "build_artifacts" / "decomposed"

    total_files: List[str] = []
    total_bytes = 0
    errors: List[str] = []

    sources_to_decompose: List[Path] = []

    # Collect source paths from context_registry
    if isinstance(registry, dict) and registry:
        for name, entry in registry.items():
            if not isinstance(entry, dict):
                continue
            raw_path = entry.get("path", "")
            if not raw_path:
                continue
            target_path = Path(raw_path)
            if not target_path.is_absolute():
                target_path = (Path(blueprint_dir) / target_path).resolve()
            if target_path.exists() and target_path.suffix == ".py":
                sources_to_decompose.append(target_path)

    # Fallback: scan workspace for Python source if no registry entries
    if not sources_to_decompose:
        for py_file in sorted(workspace.rglob("*.py")):
            # Skip test files, __init__, and build artifacts
            rel = str(py_file.relative_to(workspace)).replace("\\", "/")
            if any(skip in rel for skip in ("test_", "__pycache__", "build_artifacts", ".venv", "venv")):
                continue
            if py_file.stat().st_size > 500:  # Only non-trivial files
                sources_to_decompose.append(py_file)
                if len(sources_to_decompose) >= 5:
                    break

    for source_path in sources_to_decompose:
        # Each source gets its own sub-package inside decomposed/
        pkg_name = source_path.stem
        pkg_dir = output_dir / pkg_name
        result = decompose_source(source_path, pkg_dir, min_lines=5)
        total_files.extend(result.files_written)
        total_bytes += result.bytes_written
        errors.extend(result.errors)

        # Run the self-healing reflux pipeline on the decomposed package:
        # Pass 1 consolidates duplicate utilities into utils.py,
        # Pass 2 injects missing cross-module imports.
        if result.files_written:
            from src.decomposition.reflux import run_reflux

            reflux_result = run_reflux(pkg_dir)
            total_files.extend(reflux_result.extra_files)
            total_bytes += reflux_result.extra_bytes
            errors.extend(reflux_result.errors)

    return {
        "decomposition_files_written": total_files,
        "decomposition_file_count": len(total_files),
        "decomposition_bytes_written": total_bytes,
        "decomposition_errors": errors,
    }
