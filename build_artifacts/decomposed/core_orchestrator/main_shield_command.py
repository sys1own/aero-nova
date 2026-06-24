from __future__ import annotations
"""Auto-decomposed from monolith: function shield_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def shield_command(args: argparse.Namespace) -> int:
    """Run the precision shield validator."""
    from src.precision_shield.shield import PrecisionShield

    config = _load_blueprint_config(args.config)
    project_root = Path(args.workspace).resolve()
    shield = PrecisionShield(config)
    results = shield.validate_all(project_root)

    print("\nPrecision Shield Validation:")
    all_passed = True
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"  [{status}] {result.zone_id}")
        for v in result.violations:
            print(f"         - {v}")
        if not result.passed:
            all_passed = False
    return 0 if all_passed else 1

