from __future__ import annotations
"""Auto-decomposed from monolith: function _maybe_hardware_probe."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__workspace_json_config import _workspace_json_config
def _maybe_hardware_probe(workspace: Path) -> None:
    config = _workspace_json_config(workspace)
    if not config.get("hardware_profiling", {}).get("probe_at_compile_time"):
        return
    from src.hardware_profiling.profiler import HardwareProfiler

    print("\n[hardware] probing host...")
    try:
        profiler = HardwareProfiler(config)
        recipe = profiler.generate_recipe(profiler.probe())
        print(f"[hardware] recipe: parallelism={recipe.get('parallelism')} "
              f"unroll={recipe.get('unroll_factor')} "
              f"vectorization={recipe.get('vectorization_target', 'none')}")
    except Exception as exc:  # noqa: BLE001
        print(f"[hardware] probe skipped: {exc}")

