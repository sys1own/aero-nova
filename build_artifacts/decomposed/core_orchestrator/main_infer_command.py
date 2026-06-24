from __future__ import annotations
"""Auto-decomposed from monolith: function infer_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def infer_command(args: argparse.Namespace) -> int:
    """Infer the full execution DAG from an ultra-lean blueprint.

    Parses the few lines of semantic intent in blueprint.aero, scans the project
    directory, and prints the inferred targets, language/FFI boundaries,
    dependencies and execution order -- the graph that `build` would run with no
    further input.  With --json, emits the machine-readable inferred DAG.
    """
    from src.invisible_config import InvisibleConfigEngine, looks_like_lean_blueprint

    workspace = Path(args.workspace).resolve()
    bp_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"
    if not bp_path.exists():
        print(f"{bp_path}: blueprint file not found", file=sys.stderr)
        return 1

    content = bp_path.read_text(encoding="utf-8")
    if not looks_like_lean_blueprint(content):
        print(
            f"{bp_path}: not an ultra-lean blueprint; `infer` only applies to the "
            "Invisible Configuration dialect (project \"name\" + ingest/targets/optimize).",
            file=sys.stderr,
        )
        return 1

    engine = InvisibleConfigEngine(bp_path.parent)
    dag = engine.infer_from_source(content)

    if getattr(args, "json", False):
        print(json.dumps(dag.to_dict(), indent=2))
        return 0

    from src.build.rustflags import resolve_rustflags

    print(f"\nInferred build graph for '{dag.project}'  (mode: zero-config / invisible)")
    print(f"  optimize intent  : {dag.optimize}")
    if dag.has_invariants:
        print(f"  text invariants  : extracted from {len(dag.ingest)} ingested file(s):")
        for path in dag.ingest:
            print(f"      • {path}")
        print("      → every compiled 'core' target is made to depend on these invariants")
    else:
        print("  text invariants  : (none ingested)")

    print("\n  targets — what was detected and why:")
    for target in dag.targets:
        deps = ", ".join(target.depends_on) or "(none)"
        print(f"    ▸ {target.name}  [{target.language} / {target.role}]")
        print(f"        language : {target.language}  ({target.language_reason})")
        if target.sources:
            shown = ", ".join(target.sources[:4]) + (" …" if len(target.sources) > 4 else "")
            print(f"        sources  : {len(target.sources)} file(s) — {shown}")
        else:
            print("        sources  : none found by scanning the project tree")
        print(f"        depends  : {deps}")
        if target.language == "rust":
            decision = resolve_rustflags(optimization=dag.optimize)
            flags = decision.value if decision.inject else "(none — portable)"
            print(f"        rustflags: {flags}  [{decision.reason}]")

    print("\n  ffi / language boundaries (auto-detected):")
    if dag.ffi_boundaries:
        for boundary in dag.ffi_boundaries:
            print(f"    ▸ {boundary.provider} ({boundary.provider_language}) → "
                  f"{boundary.consumer} ({boundary.consumer_language})  via {boundary.mechanism}")
            print(f"        reason: '{boundary.consumer}' is a dynamic layer that binds the "
                  f"compiled '{boundary.provider}' core")
    else:
        print("    (none — no compiled core + dynamic consumer pair found)")

    print(f"\n  execution order  : {' → '.join(dag.topological_order())}")
    print("  self-healing     : enabled (auto-patches glue-code type mismatches, then retries)")
    print("\n  This is zero-config mode: nothing above was written by you — Aero inferred it")
    print("  from the file tree. Add an explicit blueprint to override any of it.")
    return 0

