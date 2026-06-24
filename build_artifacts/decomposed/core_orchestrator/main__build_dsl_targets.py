from __future__ import annotations
"""Auto-decomposed from monolith: function _build_dsl_targets."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__emit_polyglot_target import _emit_polyglot_target
from .main__print_build_debug import _print_build_debug
def _build_dsl_targets(
    context: dict,
    workspace: Path,
    ui: "AeroUI",
    args: argparse.Namespace,
) -> int:
    """Compile DSL blueprint targets using the compiler wrappers."""
    from error_interceptor import handle_compile_results
    from src.build.compilers import CompileResult, compile_target

    graph = context.get("graph", {})
    target_metadata = graph.get("target_metadata", [])
    build_order = graph.get("targets", [])
    dep_map = graph.get("dependencies", {})

    # Phase 3: Resolving
    # Compute parallel stages for display
    from build_graph import BuildGraph, TargetNode

    target_nodes = {}
    for m in target_metadata:
        target_nodes[m["name"]] = TargetNode(
            name=m["name"],
            language=m.get("language", ""),
            sources=m.get("sources", []),
            requires=m.get("requires", []),
            flags=m.get("flags", []),
            defines=m.get("defines", []),
            output=m.get("output"),
            optional=m.get("optional", False),
        )
    bg = BuildGraph(
        targets=target_nodes,
        dependency_map=dep_map,
        build_order=build_order,
    )
    stage_count = len(bg.levels)
    ui.resolving(len(build_order), stage_count)

    # Phase 4: Compiling each target
    results: list[CompileResult] = []
    meta_by_name = {m["name"]: m for m in target_metadata}
    debug = bool(getattr(args, "debug", False) or getattr(args, "verbose", False))
    # A build-level optimization intent (e.g. from the invisible-config `optimize`
    # word) is used as the default when a target does not set its own.
    build_optimize = (context.get("inferred_dag") or {}).get("optimize") or context.get("optimize")

    for name in build_order:
        meta = meta_by_name.get(name, {})
        language = meta.get("language", "")
        sources = meta.get("sources", [])
        output = meta.get("output")
        flags = meta.get("flags", [])
        defines = meta.get("defines", [])
        optional = meta.get("optional", False)
        target_output_language = meta.get("target_output_language", "")

        # Polyglot emitter intercept: when the target specifies a different
        # output language, route through the UAST emitter pipeline instead of
        # the standard compiler backend.
        if target_output_language and target_output_language != language:
            ui.compiling(name, f"{language} -> {target_output_language}")
            result = _emit_polyglot_target(
                target_name=name,
                source_language=language,
                target_language=target_output_language,
                sources=sources,
                output=output,
                workdir=workspace,
            )
            results.append(result)
            if debug:
                _print_build_debug(ui, name, language, result)
            if result.success:
                ui.compiled(name, target_output_language)
            elif optional:
                ui.skipped(name, "(optional, emitter unavailable)")
            else:
                ui.compile_error(name, result.error_summary)
            continue

        # Backend-specific options (e.g. Rust manifest_path / root / cargo deps,
        # and RUSTFLAGS control via optimization / rustflags).
        options = {
            "manifest_path": meta.get("manifest_path"),
            "root": meta.get("root"),
            "cargo": meta.get("cargo"),
            "cargo_dependencies": meta.get("cargo_dependencies"),
            "optimization": meta.get("optimization") or build_optimize,
            "rustflags": meta.get("rustflags"),
        }

        ui.compiling(name, language)
        result = compile_target(
            target_name=name,
            language=language,
            sources=sources,
            output=output,
            flags=flags,
            defines=defines,
            workdir=workspace,
            options=options,
        )
        results.append(result)

        if debug:
            _print_build_debug(ui, name, language, result)

        if result.success:
            ui.compiled(name, language)
        elif optional:
            ui.skipped(name, "(optional, compiler unavailable)")
        else:
            ui.compile_error(name, result.error_summary)

    # Phase 5: Report
    exit_code = handle_compile_results(
        [r for r in results if not meta_by_name.get(r.target_name, {}).get("optional", False) or not r.success],
        ui,
    )
    if exit_code == 0:
        ui.success()
    return exit_code

