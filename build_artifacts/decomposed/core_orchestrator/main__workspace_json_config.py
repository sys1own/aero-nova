from __future__ import annotations
"""Auto-decomposed from monolith: function _workspace_json_config."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _workspace_json_config(workspace: Path) -> dict:
    """Load ``blueprint_config.json`` from the workspace if present, else {}."""
    path = workspace / "blueprint_config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        logger.debug("Cannot read workspace config %s: %s", path, exc)
        return {}
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in workspace config %s: %s", path, exc)
        return {}

