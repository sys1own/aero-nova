from __future__ import annotations
"""Auto-decomposed from monolith: function runtime_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def runtime_command(args: argparse.Namespace) -> int:
    """Run the runtime benchmark and print collected metrics."""
    from src.runtime.feedback import RuntimeFeedback

    config = _load_blueprint_config(args.config)
    feedback = RuntimeFeedback(config)
    if not feedback.enabled:
        print("Runtime feedback is disabled or no benchmark_command configured.")
        return 0
    metrics = feedback.run_benchmark(workdir=str(Path(args.workspace).resolve()))
    print("\nRuntime Metrics:")
    for k, v in metrics.to_dict().items():
        print(f"  {k}: {v}")
    return 0 if metrics.success else 1

