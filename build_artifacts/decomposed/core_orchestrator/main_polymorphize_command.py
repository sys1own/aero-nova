from __future__ import annotations
"""Auto-decomposed from monolith: function polymorphize_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def polymorphize_command(args: argparse.Namespace) -> int:
    """Inspect the host and polymorphically rewrite generated code for it.

    Probes CPU vector features, cache topology, core counts and GPUs, then
    rewrites the C/C++/Rust/LLVM-IR files under --source-dir into an ephemeral
    cache (alignment, vectorised micro-kernels, thread-pool sizing) without
    touching the source directory.  With --profile-only it just prints the
    discovered topology.
    """
    from src.polymorphization import PolymorphizationEngine

    engine = PolymorphizationEngine()

    if args.profile_only:
        topology = engine.profile_host()
        derived = topology.to_dict()["derived"]
        print("\nHardware Topology:")
        print(f"  arch             : {topology.arch}")
        print(f"  cores            : {topology.physical_cores} physical / {topology.logical_cores} logical")
        print(f"  cpu features     : {', '.join(topology.cpu_features) or '(none)'}")
        print(f"  best simd        : {derived['best_simd']} ({derived['vector_width_bytes']}B vectors)")
        print(f"  cache line       : {derived['cache_line_bytes']}B  -> alignment {derived['alignment_bytes']}B")
        print(f"  cache levels     : {', '.join('L%d=%dKiB' % (c.level, c.size_bytes // 1024) for c in topology.cache_levels) or '(none)'}")
        print(f"  gpus             : {', '.join('%s/%s' % (g.runtime, g.architecture) for g in topology.gpus) or '(none)'}")
        print(f"  memory           : {topology.total_memory_bytes / 1024**3:.1f} GiB ({topology.memory_bandwidth_class} bandwidth)")
        return 0

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"{source_dir}: directory not found", file=sys.stderr)
        return 1

    cache_dir = Path(args.cache_dir)
    report = engine.polymerize_tree(source_dir, cache_dir)
    engine.write_report(report, cache_dir)

    topo = report["topology"]
    derived = topo["derived"]
    rewrite = report["rewrite"]
    print("\nAutonomous Hardware-Polymerization:")
    print(f"  host             : {topo['arch']} {topo['physical_cores']}p/{topo['logical_cores']}l")
    print(f"  best simd        : {derived['best_simd']} (align {derived['alignment_bytes']}B, {derived['vector_width_bytes']}B vectors)")
    print(f"  gpus             : {len(topo['gpus'])}")
    print(f"  files processed  : {rewrite['files_processed']}")
    print(f"  files rewritten  : {rewrite['files_rewritten']}")
    print(f"  cache (ephemeral): {cache_dir}")
    return 0

