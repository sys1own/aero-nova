from __future__ import annotations
"""Auto-decomposed from monolith: function libraries_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__load_blueprint_config import _load_blueprint_config
def libraries_command(args: argparse.Namespace) -> int:
    """Probe numerical libraries (BLAS/LAPACK/MPI/CUDA) and emit linker flags."""
    from src.build.library_tuner import LibraryTuner

    config = _load_blueprint_config(args.config)
    tuner = LibraryTuner(config)
    detected = tuner.detect_all()

    print("\nNumerical Library Detection:")
    for name, lib in detected.items():
        status = "found" if lib.found else "not found"
        extra = f" ({lib.flavor} {lib.version})".rstrip() if lib.found else ""
        print(f"  [{status:9}] {name}{extra}  via {lib.detected_via}")
        if lib.linker_flags:
            print(f"             linker: {' '.join(lib.linker_flags)}")
    print(f"\nAggregate linker flags : {' '.join(tuner.linker_flags(detected)) or '(none)'}")
    print(f"Aggregate compile flags: {' '.join(tuner.compiler_flags(detected)) or '(none)'}")
    space = tuner.genome_space(detected)
    if space:
        print("\nEvolvable library genome space:")
        for gene, values in space.items():
            print(f"  {gene}: {values}")
    return 0

