from __future__ import annotations
"""Auto-decomposed from monolith: function _registry_db_path."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _registry_db_path(args: argparse.Namespace, workspace: Path) -> Path:
    if getattr(args, "db", None):
        return Path(args.db)
    return workspace / ".aero" / "registry.db"

