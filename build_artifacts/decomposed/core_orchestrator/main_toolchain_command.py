from __future__ import annotations
"""Auto-decomposed from monolith: function toolchain_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



def toolchain_command(args: argparse.Namespace) -> int:
    """Discover, validate, and cache the host compilers/linkers/runtimes."""
    from core.toolchain import ToolchainIntrospector

    workspace = Path(args.workspace).resolve()
    blueprint_path = Path(args.blueprint) if args.blueprint else workspace / "blueprint.aero"
    introspector = ToolchainIntrospector(workspace)

    languages = [args.language] if args.language else None
    found = introspector.introspect(
        languages,
        blueprint_path=blueprint_path if languages is None else None,
        validate=not args.no_validate,
    )

    print("\nHost toolchain introspection:")
    if not found:
        print("  (no matching toolchains found on this host)")
    for lang in sorted(found):
        tc = found[lang]
        sane = "" if tc.sane is None else (" [sane]" if tc.sane else " [FAILED sanity]")
        target = f" target={tc.target}" if tc.target else ""
        print(f"  {lang}: {tc.binary} ({tc.kind}) v{tc.version or '?'}{target}{sane}")
        print(f"      path: {tc.path}")
        if tc.extra_flags or tc.compile_flags or tc.link_flags:
            print(f"      flags: extra={tc.extra_flags} compile={tc.compile_flags} link={tc.link_flags}")
        if tc.sane is False and tc.sanity_detail:
            print(f"      sanity: {tc.sanity_detail}")

    linker = introspector.discover_linker()
    if linker:
        print(f"  linker: {linker.binary} v{linker.version or '?'} ({linker.path})")
    if not args.no_validate:
        print(f"\n  cached validated configs under: {introspector.cache_dir}")
    return 0

