from __future__ import annotations
"""Auto-decomposed from monolith: function _run_ingestion_stage."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__workspace_json_config import _workspace_json_config
def _run_ingestion_stage(context: dict, workspace: Path) -> None:
    # ---- TOML living-blueprint: ingest [context_registry] entries -----------
    registry = context.get("context_registry")
    if isinstance(registry, dict) and registry:
        from src.registry.ingest import IngestError, ingest_context

        # Resolve relative paths against the blueprint's parent directory.
        blueprint_dir = Path(context.get("blueprint_dir", str(workspace)))
        db_path = workspace / ".aero" / "registry.db"
        bp_path = blueprint_dir / "blueprint.aero"

        total_files = 0
        total_errors: list = []
        for name, entry in registry.items():
            if not isinstance(entry, dict):
                continue
            raw_path = entry.get("path", "")
            if not raw_path:
                continue
            target_path = Path(raw_path)
            if not target_path.is_absolute():
                target_path = (blueprint_dir / target_path).resolve()
            language = entry.get("language") or None
            try:
                result = ingest_context(
                    name,
                    target_path,
                    language=language,
                    db_path=db_path,
                    blueprint_path=bp_path if bp_path.exists() else None,
                )
                total_files += len(result.files)
                total_errors.extend(result.errors)
            except IngestError as exc:
                total_errors.append(f"{name}: {exc}")

        print(f"\n[context] ingesting {len(registry)} context(s) from [context_registry]...")
        print(f"[context] ingested {total_files} file(s), errors {len(total_errors)}")
        for err in total_errors:
            print(f"[context]   ! {err}")
        return

    # ---- Legacy: ingest [context].sources from INI or blueprint_config.json --
    sources = (context.get("context", {}) or {}).get("sources", [])
    config = context
    if not sources:
        json_cfg = _workspace_json_config(workspace)
        sources = (json_cfg.get("context", {}) or {}).get("sources", [])
        config = json_cfg
    if not sources:
        return
    from src.context.ingest import ContextIngestor

    print(f"\n[context] ingesting {len(sources)} source tree(s)...")
    try:
        report = ContextIngestor(config, workspace).ingest_all()
        print(f"[context] ingested {report['files_ingested']} file(s), "
              f"repaired {report['files_repaired']}, errors {len(report['errors'])}")
    except Exception as exc:  # noqa: BLE001 - ingestion must not abort the build
        print(f"[context] ingestion failed: {exc}")

