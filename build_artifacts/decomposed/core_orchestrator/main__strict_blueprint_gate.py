from __future__ import annotations
"""Auto-decomposed from monolith: function _strict_blueprint_gate."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _strict_blueprint_gate(blueprint_path: Path) -> Optional[int]:
    """Strictly validate a block-format ``blueprint.aero`` before any build step.

    Returns an exit code to abort with, or ``None`` to proceed.  This is a no-op
    for the legacy INI/JSON blueprint formats (which keep their existing
    fallback behaviour); it only engages for the declarative block DSL handled by
    :mod:`blueprint_lang`, where a syntax/validation error must abort the run with
    a precise, user-friendly message before anything is built.
    """
    import blueprint_lang

    bp_path = blueprint_path
    if not bp_path.exists():
        return None
    try:
        source = bp_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Cannot read blueprint file %s: %s", bp_path, exc)
        return None
    if not blueprint_lang.looks_like_blueprint_dsl(source):
        return None
    error = blueprint_lang.check_source(source, filename=str(bp_path))
    if error is None:
        return None
    print(error, file=sys.stderr)
    print(
        "\nAborting: blueprint.aero failed strict validation; no build steps were run.",
        file=sys.stderr,
    )
    return 2

