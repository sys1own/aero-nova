from __future__ import annotations
"""Auto-decomposed from monolith: function _parse_dep_overrides."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _parse_dep_overrides(entries) -> dict:
    """Parse repeated --dep name=version flags into a {name: version} dict."""
    deps: dict = {}
    for entry in entries or []:
        if "=" in entry:
            name, _, version = entry.partition("=")
            if name.strip():
                deps[name.strip()] = version.strip()
    return deps

