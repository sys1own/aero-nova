from __future__ import annotations
"""Auto-decomposed from monolith: function _ingest_list."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__registry_db_path import _registry_db_path
def _ingest_list(args: argparse.Namespace, workspace: Path) -> int:
    """Print every ingested context in the AST registry with its semantic hash."""
    from src.registry.ast_db import ASTDatabase

    db_path = _registry_db_path(args, workspace)
    if not db_path.is_file():
        print("No AST registry found (nothing ingested yet).")
        return 0

    with ASTDatabase(db_path) as db:
        entries = db.all_entries()

    if not entries:
        print("AST registry is empty.")
        return 0

    print("\nIngested contexts:")
    by_context: dict = {}
    for entry in entries:
        by_context.setdefault(entry.context_name, []).append(entry)
    for context_name in sorted(by_context):
        files = by_context[context_name]
        print(f"  {context_name} ({len(files)} file(s)):")
        for entry in files:
            print(f"    [{entry.language}] {entry.semantic_hash[:16]}  {entry.path}")
    return 0

