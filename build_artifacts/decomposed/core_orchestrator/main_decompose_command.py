from __future__ import annotations
"""Auto-decomposed from monolith: function decompose_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def decompose_command(args: argparse.Namespace) -> int:
    """Deterministic dependency/complexity evaluator with optional auto-split."""
    from core.analysis import InferenceEngine, decompose_file
    from src.blueprint import load_blueprint

    workspace = Path(args.workspace).resolve()
    blueprint_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"
    scaling = load_blueprint(blueprint_path).scaling
    engine = InferenceEngine(workspace)

    if args.path:
        files = [Path(args.path).resolve()]
    else:
        files = engine.iter_source_files()

    analyses = engine.analyze_paths(files)
    if not analyses:
        print("No analysable source files found.")
        return 0

    print(f"\nComplexity report (max_module_complexity={scaling.max_module_complexity}, "
          f"auto_split_threshold={scaling.auto_split_threshold}):")
    for a in analyses:
        flag = " [OVERSIZED]" if a.line_count > scaling.auto_split_threshold else ""
        print(f"  {a.path} ({a.line_count} lines){flag}")
        for fn in a.functions:
            mark = "  <-- exceeds max_module_complexity" if fn.complexity > scaling.max_module_complexity else ""
            print(f"      {fn.name}: M={fn.complexity}{mark}")
        for edge in a.imports:
            target = edge.resolved or "(external/unresolved)"
            print(f"      import {edge.raw} -> {target}")

    if not args.no_dag:
        dag = engine.build_dag(analyses)
        engine.write_dag_to_blueprint(blueprint_path, dag)
        print(f"\n[dag] wrote {len(dag)} module edge-set(s) to {blueprint_path}")

    print(f"\nDecomposition ({'APPLY' if args.apply else 'dry-run'}):")
    any_action = False
    for a in analyses:
        plan = decompose_file(
            engine,
            workspace / a.path,
            max_module_complexity=scaling.max_module_complexity,
            auto_split_threshold=scaling.auto_split_threshold,
            apply=args.apply,
        )
        for action in plan.actions:
            any_action = True
            verb = "split" if plan.applied else "would split"
            print(f"  {verb} {a.path}::{action.function} -> {action.new_module} ({action.reason})")
        for skip in plan.skipped:
            print(f"  - {a.path}: {skip}")
    if not any_action:
        print("  no functions exceed the configured thresholds.")
    return 0

