from __future__ import annotations
"""Auto-decomposed from monolith: function _maybe_submit_hpc_build."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _maybe_submit_hpc_build(context: dict, workspace: Path, args: argparse.Namespace) -> bool:
    """Submit the build as a cluster job when HPC is enabled. Returns True if so."""
    from src.hpc.scheduler import HPCScheduler

    scheduler = HPCScheduler(context)
    if not scheduler.enabled or scheduler.build_on_login_node:
        return False
    if not scheduler.available():
        print(f"[hpc] {scheduler.scheduler} CLI not found; building locally instead.")
        return False

    import shlex
    build_cmd = f"python main.py build --workspace {shlex.quote(str(workspace))} --no-hpc --cycles {int(args.cycles)}"
    commands = [build_cmd]
    if scheduler.post_build_run and context.get("runtime", {}).get("benchmark_command"):
        commands.append(context["runtime"]["benchmark_command"])

    job = scheduler.submit(commands, job_name="aero_build", workdir=str(workspace))
    if not job.submitted:
        print(f"[hpc] submission failed ({job.error}); building locally instead.")
        return False
    print(f"[hpc] submitted build job {job.job_id} to {scheduler.scheduler}; waiting...")
    job = scheduler.wait(job)
    print(f"[hpc] build job {job.job_id} finished with state {job.state}")
    return job.succeeded

