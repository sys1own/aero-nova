from __future__ import annotations
"""Auto-decomposed from monolith: function _run_validation_stage."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _run_validation_stage(context: dict, workspace: Path) -> int:
    from src.validation.validator import Validator

    validator = Validator(context)
    if not validator.enabled:
        return 0
    print("\n[validation] running suite...")
    report = validator.run(workdir=str(workspace))
    for case in report.cases:
        print(f"  [{'PASS' if case.passed else 'FAIL'}] {case.name}")
    print(f"[validation] {report.summary}")
    if not report.passed and validator.is_gatekeeper:
        print("[validation] FAILED (gatekeeper) -> build marked unsuccessful")
        return 1
    return 0

