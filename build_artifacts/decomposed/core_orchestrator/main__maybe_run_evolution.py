from __future__ import annotations
"""Auto-decomposed from monolith: function _maybe_run_evolution."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__workspace_json_config import _workspace_json_config
def _maybe_run_evolution(workspace: Path) -> None:
    config_path = workspace / "blueprint_config.json"
    config = _workspace_json_config(workspace)
    if not config.get("project", {}).get("evolutionary_bootstrap", {}).get("enabled"):
        return
    from src.evolution.bootstrap import SelfEvolutionEngine

    print("\n[evolution] running bounded self-evolution pass...")
    try:
        engine = SelfEvolutionEngine(config_path, workspace)
        best = engine.evolve(max_generations=min(3, engine.max_generations))
        print(f"[evolution] best candidate {best.id} fitness={ {k: round(v, 2) for k, v in best.fitness.items()} }")
    except Exception as exc:  # noqa: BLE001
        print(f"[evolution] skipped: {exc}")

