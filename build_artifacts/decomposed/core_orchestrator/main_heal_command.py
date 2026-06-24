from __future__ import annotations
"""Auto-decomposed from monolith: function heal_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def heal_command(args: argparse.Namespace) -> int:
    """Run the deterministic self-healing build loop on a module."""
    from core.toolchain.self_healing import heal_module, make_c_build_fn, make_rust_build_fn

    workspace = Path(args.workspace).resolve()
    target = Path(args.path).resolve()
    blueprint_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"

    language = args.language
    if language is None:
        from core.parser.universal import detect_language

        language = detect_language(target)

    if language == "rust":
        build_fn = make_rust_build_fn()
    elif language in ("c", "cpp"):
        build_fn = make_c_build_fn("cc" if language == "c" else "c++")
    else:
        print(f"heal: no compiler build driver for language {language!r}", file=sys.stderr)
        return 1

    report = heal_module(
        target, build_fn,
        language=language, workspace=workspace, blueprint_path=blueprint_path,
        max_attempts=args.max_attempts,
    )

    print(f"\nSelf-healing: {report.path}")
    print(f"  build attempts : {report.attempts} (budget {args.max_attempts})")
    print(f"  applied fixes  : {', '.join(report.applied) or '(none)'}")
    if report.success:
        print("  result         : CLEAN BUILD")
        return 0
    print("  result         : FAILED")
    if report.rolled_back:
        print(f"  rolled back    : yes ({report.reason})")
        print(f"  flagged in     : {blueprint_path} [self_healing]")
    for d in report.final_diagnostics[:10]:
        print(f"    [{d.code or '?'}] {d.message}")
    return 1

