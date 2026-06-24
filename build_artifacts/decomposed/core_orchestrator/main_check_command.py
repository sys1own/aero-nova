from __future__ import annotations
"""Auto-decomposed from monolith: function check_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def check_command(args: argparse.Namespace) -> int:
    """Strictly validate a block-format ``blueprint.aero`` without building.

    Prints an ultra-clear ``line:column`` + ``^`` diagnostic on failure and
    exits non-zero, so it can gate a build pipeline.
    """
    import blueprint_lang

    workspace = Path(args.workspace).resolve()
    bp_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"
    if not bp_path.exists():
        print(f"{bp_path}: blueprint file not found", file=sys.stderr)
        return 1

    source = bp_path.read_text(encoding="utf-8")
    if source.strip() and not blueprint_lang.looks_like_blueprint_dsl(source):
        # TOML living-blueprint ([system] / [context_registry]) is a first-class
        # format — validate it via the TOML loader rather than dismissing it.
        from blueprint_parser import _looks_like_toml_native
        if _looks_like_toml_native(source):
            try:
                from src.blueprint.loader import LivingBlueprint
                LivingBlueprint.from_str(source)
                print(f"{bp_path}: OK -- TOML living-blueprint is valid")
                return 0
            except Exception as exc:
                print(f"{bp_path}: TOML blueprint validation failed: {exc}", file=sys.stderr)
                return 1
        print(
            f"{bp_path}: INI/JSON blueprint detected; the strict DSL "
            "checker only validates block-format blueprints. "
            "Use 'python main.py build' to exercise INI/JSON blueprints."
        )
        return 0

    error = blueprint_lang.check_source(source, filename=str(bp_path))
    if error is None:
        print(f"{bp_path}: OK -- blueprint is valid")
        return 0
    print(error, file=sys.stderr)
    return 1

