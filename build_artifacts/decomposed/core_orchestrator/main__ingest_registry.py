from __future__ import annotations
"""Auto-decomposed from monolith: function _ingest_registry."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__registry_db_path import _registry_db_path
def _ingest_registry(args: argparse.Namespace, workspace: Path) -> int:
    """Parse a file/tree into the AST registry and register it in the blueprint."""
    from src.registry.ingest import IngestError, ingest_context

    source_path = Path(args.path).resolve()
    context_name = args.context_name
    if not context_name:
        base = source_path if source_path.is_dir() else source_path.parent
        context_name = base.name or "context"

    blueprint_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"
    db_path = _registry_db_path(args, workspace)

    try:
        result = ingest_context(
            context_name,
            source_path,
            language=args.language,
            db_path=db_path,
            blueprint_path=blueprint_path,
        )
    except IngestError as exc:
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        return 1

    print(f"\nIngested context '{result.context_name}':")
    print(f"  files ingested : {len(result.files)}")
    for fr in result.files:
        print(f"    [{fr.language}] {fr.semantic_hash[:16]}  {fr.path}")
        if fr.functions:
            print(f"        functions: {', '.join(fr.functions)}")
        if fr.types:
            print(f"        types    : {', '.join(fr.types)}")
    if result.blueprint_updated:
        print(f"  blueprint      : registered [context_registry.{result.context_name}] in {blueprint_path}")
    elif result.files:
        print(f"  blueprint      : '{result.context_name}' already registered")
    if result.errors:
        print("  errors:")
        for err in result.errors:
            print(f"    ! {err}")
    print(f"  registry       : {db_path}")
    return 0 if not result.errors else 1

