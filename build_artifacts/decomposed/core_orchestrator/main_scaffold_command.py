from __future__ import annotations
"""Auto-decomposed from monolith: function scaffold_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__parse_dep_overrides import _parse_dep_overrides
def scaffold_command(args: argparse.Namespace) -> int:
    """Generate a complete, out-of-tree standalone repo from a source entry.

    Resolves --source-entry from anywhere on the filesystem, shields rug/pyo3
    sources with the codified compatibility fixes, and writes a turn-key
    Cargo project (Cargo.toml / src/lib.rs / .gitignore / README.md /
    test_binding.py) into a temp dir or the given --distribution-directory --
    never touching the aero-universal tree.  With --build, compiles it via cargo
    (from the generated repo) using the diagnostic-recovery retry loop.
    """
    from src.scaffold import ScaffoldEngine
    from src.scaffold.source_resolver import SourceEntryNotFound
    from src.scaffold.workspace import WorkspaceLocationError

    verbose = bool(getattr(args, "verbose", False))
    engine = ScaffoldEngine(logger=lambda m: print(f"  [scaffold] {m}"), verbose=verbose)

    deps = _parse_dep_overrides(getattr(args, "dep", None))
    print(f"\nScaffolding standalone repository from: {args.source_entry}")
    try:
        result = engine.scaffold(
            source_entry=args.source_entry,
            name=args.name,
            distribution_directory=args.distribution_directory,
            dependencies=deps or None,
            build=bool(getattr(args, "build", False)),
            keep=True if args.distribution_directory else not getattr(args, "no_keep", False),
            merge_active=bool(getattr(args, "merge_active", False)),
        )
    except SourceEntryNotFound as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except WorkspaceLocationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    repo = result.repo
    shield = result.shield
    spec = repo.get('spec', {})
    print("\nStandalone repository generated:")
    print(f"  location         : {result.workspace}  (out-of-tree)")
    print(f"  project          : {spec.get('name', '-')}  v{spec.get('version', '0.0.0')}  ({result.language})")
    print(f"  dependencies     : {', '.join(spec.get('dependencies') or []) or '(none)'}")
    if spec.get('crate_type'):
        print(f"  crate-type       : {spec['crate_type']}")
    if spec.get('python_module'):
        print(f"  python module    : {spec['python_module']}")
    print(f"  files written    : {', '.join(repo.get('files') or [])}")
    if shield['anchors']:
        applied = ', '.join(shield['applied']) or '(already compatible)'
        print(f"  semantic shields : anchors={shield['anchors']} -> {applied}")
    if result.build is not None:
        build = result.build
        if build.get("bypassed"):
            print(f"  build            : bypassed — {build.get('warning', 'non-rust target')}")
        else:
            status = "succeeded" if build["succeeded"] else "failed"
            note = " (recovered after auto-correction)" if build.get("recovered") else ""
            print(f"  build            : {status}{note} in {len(build['attempts'])} attempt(s)")
    if result.merge is not None:
        merge = result.merge
        if merge.get("merged"):
            live = "loaded live in-process" if merge.get("loaded") else "staged for next start"
            print(f"  active merge     : {merge['module_name']} -> {merge['destination']} ({live})")
        else:
            print(f"  active merge     : skipped — {merge.get('reason', 'unavailable')}")
    print(f"\n  Push it as-is:  cd {result.workspace} && git init && git add . && git commit -m 'init'")
    if result.merge is not None and result.merge.get("merged"):
        print(f"  Now importable:  python3 -c \"import {result.merge['module_name']}\"")
    return 0 if (result.build is None or result.build["succeeded"]) else 1

