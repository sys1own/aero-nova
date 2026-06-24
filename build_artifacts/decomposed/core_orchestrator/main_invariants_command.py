from __future__ import annotations
"""Auto-decomposed from monolith: function invariants_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def invariants_command(args: argparse.Namespace) -> int:
    """Ingest unstructured context + source files into the Invariant Schema.

    Reads every .txt/.md/.pdf/.json/.cpp/.py file under --source-dir, extracts
    state variables, algorithmic boundaries and equations per domain, and
    writes the result (plus the cross-domain system graph) as a JSON
    compilation input for downstream code generator nodes.
    """
    from src.semantic_fluidity import ContextIngestionEngine

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"{source_dir}: directory not found", file=sys.stderr)
        return 1

    workspace = Path(args.workspace).resolve()
    output_path = Path(args.output) if args.output else workspace / ContextIngestionEngine.REPORT_NAME

    engine = ContextIngestionEngine()
    payload = engine.ingest_and_export(source_dir, output_path)
    schema = payload["invariant_schema"]

    print("\nSemantic Fluidity Ingestion:")
    print(f"  domains          : {', '.join(schema['domains']) or '(none)'}")
    print(f"  state variables  : {len(schema['state_variables'])}")
    print(f"  boundaries       : {len(schema['boundaries'])}")
    print(f"  equations        : {len(schema['equations'])}")
    print(f"  system graph     : {payload['graph_statistics']['node_count']} node(s), "
          f"{payload['graph_statistics']['edge_count']} edge(s), "
          f"{payload['graph_statistics']['cross_domain_edges']} cross-domain edge(s)")
    if payload["ingestion_errors"]:
        print("  errors:")
        for err in payload["ingestion_errors"]:
            print(f"    ! {err}")
    print(f"  report           : {output_path}")
    return 0

