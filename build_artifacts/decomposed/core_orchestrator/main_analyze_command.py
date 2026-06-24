from __future__ import annotations
"""Auto-decomposed from monolith: function analyze_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def analyze_command(args: argparse.Namespace) -> int:
    """Run the semantic proximity mapping engine."""
    from src.analysis.semantic_mapper import SemanticMapper

    config = _load_blueprint_config(args.config)
    project_root = Path(args.workspace).resolve()
    mapper = SemanticMapper(config)
    mapper.build_uast(project_root)

    stats = mapper.get_statistics()
    print("\nSemantic Analysis complete.")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    if args.export:
        export_path = Path(args.export)
        mapper.export_graph(export_path)
        print(f"  UAST exported to {export_path}")
    return 0

