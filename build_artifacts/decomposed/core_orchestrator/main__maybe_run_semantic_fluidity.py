from __future__ import annotations
"""Auto-decomposed from monolith: function _maybe_run_semantic_fluidity."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__workspace_json_config import _workspace_json_config
def _maybe_run_semantic_fluidity(workspace: Path) -> None:
    """Ingest unstructured context (papers, prose, code) into the Invariant
    Schema and write it to the workspace as a high-level compilation input for
    downstream code generator nodes.  Opt-in via blueprint_config.json's
    ``semantic_fluidity`` section; never aborts the build on failure.
    """
    config = _workspace_json_config(workspace)
    fluidity_cfg = config.get("semantic_fluidity", {})
    if not fluidity_cfg.get("enabled"):
        return
    source_dir = workspace / fluidity_cfg.get("source_dir", "context_sources")
    if not source_dir.exists():
        return
    from src.semantic_fluidity import ContextIngestionEngine

    print(f"\n[semantic-fluidity] ingesting {source_dir}...")
    try:
        engine = ContextIngestionEngine()
        output_path = workspace / ContextIngestionEngine.REPORT_NAME
        payload = engine.ingest_and_export(source_dir, output_path)
        schema = payload["invariant_schema"]
        print(
            f"[semantic-fluidity] {len(schema['domains'])} domain(s), "
            f"{len(schema['state_variables'])} state var(s), "
            f"{len(schema['equations'])} equation(s), "
            f"{len(schema['boundaries'])} boundary rule(s) -> {output_path}"
        )
    except Exception as exc:  # noqa: BLE001 - ingestion must not abort the build
        print(f"[semantic-fluidity] ingestion skipped: {exc}")

