from __future__ import annotations
"""Auto-decomposed from monolith: function _print_build_debug."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def _print_build_debug(ui: "AeroUI", name: str, language: str, result) -> None:
    """Print --debug detail for a compiled target (manifest, command, env, deps).

    Surfaces exactly what Aero used so version-mismatch and RUSTFLAGS issues are
    diagnosable without guesswork (Rust targets carry the richest detail).
    """
    details = result.details or {}
    ui.debug(f"{name}: language={language or 'unknown'}")
    command = details.get("command")
    if command:
        ui.debug(f"{name}: cargo command: {' '.join(str(c) for c in command)}")
    env = details.get("env") or {}
    if env:
        ui.debug(f"{name}: env: " + " ".join(f"{k}={v}" for k, v in env.items()))
    else:
        ui.debug(f"{name}: env: (no RUSTFLAGS injected)")
    rustflags = details.get("rustflags") or {}
    if rustflags:
        ui.debug(f"{name}: RUSTFLAGS policy: {rustflags.get('reason', '')}")
    if "crate_root" in details:
        origin = "existing" if details.get("used_existing") else "synthesised"
        ui.debug(f"{name}: crate root: {details['crate_root']} (manifest: {origin})")
    deps = details.get("declared_dependencies")
    if deps:
        ui.debug(f"{name}: dependencies: " + ", ".join(f"{k}={v}" for k, v in deps.items()))
    manifest = details.get("manifest")
    if manifest:
        ui.debug_block(f"{name}: Cargo.toml in use", manifest.rstrip().splitlines())

