from __future__ import annotations
"""Auto-decomposed from monolith: function profile_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def profile_command(args: argparse.Namespace) -> int:
    """Run the hardware profiling engine."""
    from src.hardware_profiling.profiler import HardwareProfiler

    config = _load_blueprint_config(args.config)
    profiler = HardwareProfiler(config)
    profile = profiler.probe()
    saved = profiler.save_profile(profile)
    recipe = profiler.generate_recipe(profile)

    print(f"\nHardware Profile saved to {saved}")
    print(f"  CPU: {profile.cpu_model}  ({profile.cpu_count} cores)")
    print(f"  Arch: {profile.arch}")
    print(f"  Memory: {profile.total_memory_bytes / 1024**3:.1f} GB")
    print(f"  Cache levels: {len(profile.cache_hierarchy)}")
    print(f"  SIMD sets: {[s.instruction_set for s in profile.simd_capabilities if s.available]}")
    print(f"\nGenerated recipe:")
    for k, v in recipe.items():
        print(f"  {k}: {v}")
    return 0

