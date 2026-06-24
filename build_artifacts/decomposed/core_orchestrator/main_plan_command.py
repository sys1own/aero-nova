from __future__ import annotations
"""Auto-decomposed from monolith: function plan_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def plan_command(args: argparse.Namespace) -> int:
    """Auto-discover ``blueprint.aero``, validate, build the DAG, and print a visual tree.

    This is the quick-feedback command: no compilation happens, just parsing,
    validation, dependency resolution, and a clean tree of what the build
    *would* do.  Supports both the block DSL and the legacy INI format.
    """
    import blueprint_lang
    from aero_ui import AeroUI
    from build_graph import blueprint_to_dag
    from src.build.compilers import get_backend

    ui = AeroUI()
    workspace = Path(args.workspace).resolve()
    bp_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"

    if not bp_path.exists():
        print(f"{bp_path}: blueprint file not found", file=sys.stderr)
        return 1

    source = bp_path.read_text(encoding="utf-8")

    if blueprint_lang.looks_like_blueprint_dsl(source):
        ui.parsing(str(bp_path))
        error = blueprint_lang.check_source(source, filename=str(bp_path))
        if error is not None:
            print(error, file=sys.stderr)
            return 2

        blueprint = blueprint_lang.load_source(source, filename=str(bp_path))
        graph = blueprint_to_dag(blueprint)
        ui.validating(len(graph.build_order))
        ui.resolving(len(graph.build_order), len(graph.levels))

        # Show compiler availability per target
        for name in graph.build_order:
            node = graph.targets[name]
            backend = get_backend(node.language)
            binary = backend.discover() if backend else None
            status = binary or "not found"
            ui.plan(f"{name} ({node.language}) -> {status}")

        print()
        print(graph.render_tree())
        return 0

    # Legacy INI/JSON -- parse through blueprint_parser and summarise.
    import blueprint_parser

    ui.parsing(str(bp_path))
    context = blueprint_parser.parse_blueprint(str(bp_path))
    if context.get("workspace_status") == "reverted_fallback":
        print(f"blueprint validation failed: {context.get('fallback_reason')}", file=sys.stderr)
        return 2

    graph_section = context.get("graph", {})
    targets = graph_section.get("targets", [])
    deps = graph_section.get("dependencies", {})
    metadata = graph_section.get("target_metadata", [])
    meta_by_name = {m.get("name", ""): m for m in metadata} if metadata else {}
    ui.validating(len(targets))

    header = "Build Plan (legacy INI/JSON)"
    lines = [header, "=" * len(header)]
    for idx, name in enumerate(targets, 1):
        is_last = idx == len(targets)
        connector = "└── " if is_last else "├── "
        continuation = "    " if is_last else "│   "
        meta = meta_by_name.get(name, {})
        source_info = meta.get("source", "")
        lines.append(f"{connector}{idx}. {name}")
        target_deps = deps.get(name, [])
        if target_deps:
            lines.append(f"{continuation}requires: {', '.join(target_deps)}")
        if source_info:
            lines.append(f"{continuation}source:   {source_info}")
    lines.append("")
    lines.append(f"{len(targets)} target{'s' if len(targets) != 1 else ''}")
    print("\n".join(lines))
    return 0

