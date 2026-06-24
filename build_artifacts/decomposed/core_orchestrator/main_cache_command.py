from __future__ import annotations
"""Auto-decomposed from monolith: function cache_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def cache_command(args: argparse.Namespace) -> int:
    """Show or clear the memoization cache."""
    from src.memoization.cache_engine import MemoizationEngine

    config = _load_blueprint_config(args.config)
    engine = MemoizationEngine(config)

    if args.action == "stats":
        s = engine.stats()
        print("\nMemoization Cache stats:")
        for k, v in s.items():
            print(f"  {k}: {v}")
    elif args.action == "clear":
        engine.cache.clear()
        print("Cache cleared.")
    elif args.action == "cycles":
        cycles = engine.check_dependency_cycles()
        if cycles:
            print(f"Detected {len(cycles)} dependency cycle(s):")
            for c in cycles:
                print(f"  {' -> '.join(c)}")
        else:
            print("No dependency cycles detected.")
    return 0

