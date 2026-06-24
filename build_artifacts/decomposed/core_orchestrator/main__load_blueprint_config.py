from __future__ import annotations
"""Auto-decomposed from monolith: function _load_blueprint_config."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _load_blueprint_config(path: Optional[str] = None) -> dict:
    p = Path(path) if path else _BLUEPRINT_CONFIG
    if not p.exists():
        print(f"Blueprint config not found: {p}", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))

