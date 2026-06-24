from __future__ import annotations
"""Auto-decomposed from monolith: function ingest_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__ingest_list import _ingest_list
from .main__ingest_registry import _ingest_registry
from .main__load_blueprint_config import _load_blueprint_config
def ingest_command(args: argparse.Namespace) -> int:
    """Ingest source into the AST registry, or external trees from [context]."""
    workspace = Path(args.workspace).resolve()

    # New living-blueprint registry modes.
    if getattr(args, "list", False):
        return _ingest_list(args, workspace)
    if getattr(args, "path", None):
        return _ingest_registry(args, workspace)

    # Legacy behaviour: ingest the source trees declared in [context].
    from src.context.ingest import ContextIngestor

    config = _load_blueprint_config(args.config)
    ingestor = ContextIngestor(config, workspace)
    report = ingestor.ingest_all()

    print("\nContext Ingestion:")
    print(f"  sources        : {report['source_count']}")
    print(f"  files ingested : {report['files_ingested']}")
    print(f"  files repaired : {report['files_repaired']}")
    for src in report["sources"]:
        status = src["error"] or f"{src['files_ingested']} file(s) -> {src['target_mapping']}"
        print(f"    - {src['path']}: {status}")
    if report["errors"]:
        print("  errors:")
        for err in report["errors"]:
            print(f"    ! {err}")
    print(f"  report         : {workspace / ContextIngestor.REPORT_NAME}")
    return 0 if not report["errors"] else 1

