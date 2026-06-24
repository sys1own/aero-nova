from __future__ import annotations
"""Auto-decomposed from monolith: function commit_overlay_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def commit_overlay_command(args: argparse.Namespace) -> int:
    """Capture manual edits to a generated file as a reusable overlay patch."""
    from src.overlay import OverlayError, OverlayManager

    workspace = Path(args.workspace).resolve()
    target = Path(args.file).resolve()
    manager = OverlayManager(workspace)

    try:
        patch = manager.commit_overlay(target)
    except OverlayError as exc:
        print(f"commit-overlay failed: {exc}", file=sys.stderr)
        return 1

    key = manager.store.relkey(target)
    if patch is None:
        print(f"No manual edits detected in {key}; nothing to commit.")
        return 0
    overlay_path = manager.store.overlay_path(target)
    line_count = sum(1 for ln in patch.splitlines() if ln[:1] in ("+", "-") and not ln.startswith(("+++", "---")))
    print(f"Committed overlay for {key} ({line_count} changed line(s)).")
    print(f"  saved to: {overlay_path}")
    return 0

