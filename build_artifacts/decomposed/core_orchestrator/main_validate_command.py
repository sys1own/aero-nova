from __future__ import annotations
"""Auto-decomposed from monolith: function validate_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def validate_command(args: argparse.Namespace) -> int:
    """Run the validation suite against the built artefacts."""
    from src.validation.validator import Validator

    config = _load_blueprint_config(args.config)
    validator = Validator(config)
    if not validator.enabled:
        print("No validation.execution_command configured.")
        return 0
    report = validator.run(workdir=str(Path(args.workspace).resolve()))
    print("\nValidation Report:")
    for case in report.cases:
        print(f"  [{'PASS' if case.passed else 'FAIL'}] {case.name}")
    print(f"  {report.summary}")
    return 0 if report.passed else 1

