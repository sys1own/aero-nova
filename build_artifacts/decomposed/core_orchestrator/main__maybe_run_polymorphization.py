from __future__ import annotations
"""Auto-decomposed from monolith: function _maybe_run_polymorphization."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__workspace_json_config import _workspace_json_config
def _maybe_run_polymorphization(workspace: Path) -> None:
    """Probe the host and polymorphically rewrite the generated sources for it.

    Runs after code generation but before linking/execution.  Operates on the
    generated artifacts directory and writes rewritten copies into an ephemeral
    build cache (``.aero/polymorph_cache``), leaving the user's primary source
    directory untouched.  On by default (no flags required); can be disabled via
    ``--no-polymorph`` or ``blueprint_config.json``'s ``polymorphization`` section.
    Never aborts the build on failure.
    """
    config = _workspace_json_config(workspace)
    poly_cfg = config.get("polymorphization", {})
    if poly_cfg.get("enabled") is False:
        return
    source_dir = workspace / poly_cfg.get("source_dir", "build_artifacts")
    if not source_dir.exists():
        return
    from src.polymorphization import PolymorphizationEngine

    cache_dir = workspace / poly_cfg.get("cache_dir", str(Path(".aero") / "polymorph_cache"))
    print(f"\n[polymorph] inspecting host and rewriting {source_dir}...")
    try:
        engine = PolymorphizationEngine()
        report = engine.polymerize_tree(source_dir, cache_dir)
        engine.write_report(report, cache_dir)
        topo = report["topology"]
        derived = topo["derived"]
        rewrite = report["rewrite"]
        print(
            f"[polymorph] host: {topo['arch']} {topo['physical_cores']}p/{topo['logical_cores']}l "
            f"simd={derived['best_simd']} align={derived['alignment_bytes']}B "
            f"gpus={len(topo['gpus'])}"
        )
        print(
            f"[polymorph] rewrote {rewrite['files_rewritten']}/{rewrite['files_processed']} "
            f"file(s) -> {cache_dir}"
        )
    except Exception as exc:  # noqa: BLE001 - polymorphization must not abort the build
        print(f"[polymorph] skipped: {exc}")

