from __future__ import annotations
"""Auto-decomposed from monolith: function _emit_polyglot_target."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _emit_polyglot_target(
    target_name: str,
    source_language: str,
    target_language: str,
    sources: list,
    output: str | None,
    workdir: Path,
) -> "CompileResult":
    """Parse source files into UAST and emit translated code via the emitter.

    When a blueprint target sets ``target_output_language`` to a language that
    differs from the source ``language``, this function is called instead of the
    standard compilation backend.  It:

    1. Resolves source globs against the workspace.
    2. Parses each source file into a UAST via the universal parser.
    3. Instantiates the registered emitter for the target language.
    4. Writes the translated output to disk (either the explicit ``output`` path
       or ``build_artifacts/<target_name>.<ext>``).
    """
    import glob as _glob

    from src.build.compilers import CompileResult
    from core.parser.universal import parse_file, UniversalParseError
    from builder_brains.emitters import get_emitter, EmitterError

    # Language -> file extension mapping for output files.
    _EXT_MAP = {
        "python": ".py",
        "rust": ".rs",
        "cpp": ".cpp",
        "c": ".c",
        "fortran": ".f90",
    }

    resolved_files: list[Path] = []
    for pattern in sources:
        matches = sorted(_glob.glob(str(workdir / pattern), recursive=True))
        resolved_files.extend(Path(m) for m in matches if Path(m).is_file())

    if not resolved_files:
        return CompileResult(
            target_name=target_name,
            success=False,
            command=["emitter"],
            stderr=f"No source files found for patterns: {sources}",
        )

    all_nodes: list[dict] = []
    scope_graph: dict = {}

    for src_file in resolved_files:
        try:
            uast = parse_file(src_file, language=source_language)
        except UniversalParseError as exc:
            return CompileResult(
                target_name=target_name,
                success=False,
                command=["emitter", str(src_file)],
                stderr=f"UAST parse error for {src_file}: {exc}",
            )
        nodes = uast.get("nodes", [])
        if nodes:
            all_nodes.extend(nodes)

    if not all_nodes:
        return CompileResult(
            target_name=target_name,
            success=False,
            command=["emitter"],
            stderr="UAST is empty after parsing all source files.",
        )

    try:
        emitter = get_emitter(
            target_language,
            all_nodes,
            scope_graph=scope_graph,
            source_language=source_language,
        )
        translated_code = emitter.emit()
    except EmitterError as exc:
        return CompileResult(
            target_name=target_name,
            success=False,
            command=["emitter", target_language],
            stderr=str(exc),
        )

    ext = _EXT_MAP.get(target_language, ".out")
    if output:
        out_path = workdir / output
    else:
        out_dir = workdir / "build_artifacts"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{target_name}{ext}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(translated_code, encoding="utf-8")

    return CompileResult(
        target_name=target_name,
        success=True,
        command=["emitter", source_language, "->", target_language],
        stdout=f"Translated {len(resolved_files)} file(s) -> {out_path}",
        output_path=str(out_path),
        details={
            "source_language": source_language,
            "target_language": target_language,
            "source_files": [str(f) for f in resolved_files],
            "node_count": len(all_nodes),
        },
    )

