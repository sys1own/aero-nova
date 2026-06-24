from __future__ import annotations
"""Auto-decomposed from monolith: function _run_runtime_stage."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _run_runtime_stage(context: dict, workspace: Path) -> None:
    from src.runtime.feedback import RuntimeFeedback

    feedback = RuntimeFeedback(context)
    if not feedback.enabled:
        return
    print("\n[runtime] running benchmark...")
    metrics = feedback.run_benchmark(workdir=str(workspace))
    if metrics.success:
        print(f"[runtime] wall_time={metrics.wall_time:.4f}s "
              f"cpu_time={metrics.cpu_time:.4f}s peak_rss={metrics.peak_rss_mb:.1f}MB")
        if metrics.accuracy_error is not None:
            print(f"[runtime] accuracy_error={metrics.accuracy_error:.3e}")
    else:
        print(f"[runtime] benchmark did not succeed: {metrics.error}")

