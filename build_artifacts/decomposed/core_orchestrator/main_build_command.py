from __future__ import annotations
"""Auto-decomposed from monolith: function build_command."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main__build_dsl_targets import _build_dsl_targets
from .main__maybe_hardware_probe import _maybe_hardware_probe
from .main__maybe_run_evolution import _maybe_run_evolution
from .main__maybe_run_polymorphization import _maybe_run_polymorphization
from .main__maybe_run_semantic_fluidity import _maybe_run_semantic_fluidity
from .main__maybe_submit_hpc_build import _maybe_submit_hpc_build
from .main__run_ingestion_stage import _run_ingestion_stage
from .main__run_runtime_stage import _run_runtime_stage
from .main__run_validation_stage import _run_validation_stage
from .main__strict_blueprint_gate import _strict_blueprint_gate
def build_command(args: argparse.Namespace) -> int:
    import blueprint_parser
    from aero_ui import AeroUI
    from error_interceptor import handle_compile_results

    ui = AeroUI()
    orchestrator.configure_logging(verbose=args.verbose)
    workspace = Path(args.workspace).resolve()
    bp_path = Path(args.blueprint).resolve() if getattr(args, "blueprint", None) else workspace / "blueprint.aero"

    # Phase 1: Parsing
    ui.parsing(str(bp_path))

    # Strict syntax/validation gate -- runs BEFORE any build step so a broken
    # block-format blueprint aborts immediately with a clear diagnostic.
    gate = _strict_blueprint_gate(bp_path)
    if gate is not None:
        return gate

    context = blueprint_parser.parse_blueprint(str(bp_path))

    # Isolated scaffold build: when [scaffold] declares auto_layout and/or
    # source_entry, route through the out-of-tree pipeline and keep the tool
    # directory pristine.
    from src.scaffold.pipeline import ScaffoldBuildPipeline, should_run_scaffold_pipeline
    from src.scaffold.source_resolver import SourceEntryNotFound
    from src.scaffold.workspace import WorkspaceLocationError

    if should_run_scaffold_pipeline(context) and not getattr(args, "validation_only", False):
        ui.tag("Scaffold", "out-of-tree isolated build from blueprint [scaffold]")
        blueprint_dir = bp_path.parent
        pipeline = ScaffoldBuildPipeline(verbose=args.verbose or True)
        try:
            result = pipeline.run(
                context,
                blueprint_dir=blueprint_dir,
                build=not getattr(args, "no_scaffold_build", False),
            )
        except (SourceEntryNotFound, WorkspaceLocationError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        repo = result.scaffold.repo
        spec = repo.get("spec") or {}
        print("\nIsolated scaffold build complete:")
        print(f"  language         : {result.language}")
        print(f"  workspace        : {result.scaffold.workspace}  (out-of-tree)")
        if result.language == "python":
            print(f"  project          : {spec.get('name', '?')}")
            print(f"  entry script     : {spec.get('entry_filename', '?')}")
        else:
            print(f"  crate            : {spec.get('name', '?')}  v{spec.get('version', '?')}")
        print(f"  files written    : {', '.join(repo.get('files', []))}")
        if result.scaffold.shield.get("applied"):
            print(f"  shields applied  : {', '.join(result.scaffold.shield['applied'])}")
        elif result.language == "python":
            print("  shields applied  : (skipped — Python target)")
        if result.scaffold.build is not None:
            label = "validation" if result.language == "python" else "build"
            status = "succeeded" if result.scaffold.build["succeeded"] else "failed"
            print(f"  {label:16} : {status}")
        ui.success()
        return 0 if result.succeeded else 1

    # Phase 2: Validating
    targets = context.get("compilation_targets", [])
    is_dsl = context.get("blueprint_format") == "dsl"
    ui.validating(len(targets))

    # If DSL format, resolve the build graph and compile targets.
    if is_dsl and not getattr(args, "validation_only", False):
        return _build_dsl_targets(context, workspace, ui, args)

    # --validation-only: skip the build entirely and just run the suite.
    if getattr(args, "validation_only", False):
        return _run_validation_stage(context, workspace)

    # Context ingestion runs before the build so imported sources are present.
    _run_ingestion_stage(context, workspace)

    # Domain-agnostic semantic fluidity: ingest unstructured context into the
    # Invariant Schema, exposed to code generator nodes as a compilation input.
    _maybe_run_semantic_fluidity(workspace)

    # Hardware profiling at the start of the build cycle (feature #6).
    if not getattr(args, "no_hardware_probe", False):
        _maybe_hardware_probe(workspace)

    # HPC integration: optionally submit the build to a cluster (feature #1).
    ran_on_cluster = False
    if not getattr(args, "no_hpc", False):
        ran_on_cluster = _maybe_submit_hpc_build(context, workspace, args)

    if not ran_on_cluster:
        ui.tag("Compiling", f"{len(targets)} target(s) via orchestrator")
        metadata = orchestrator.run_build(
            workspace_root=str(workspace),
            cycles=args.cycles,
            telemetry_interval=args.telemetry_interval,
            bootstrap_active=getattr(args, "bootstrap_active", False),
        )
        ui.success()
        print(f"Manifest: {metadata.get('manifest_path')}")
        for asset in metadata.get("applied_assets", []):
            print(f"Updated asset: {asset}")

    # Overlay system: re-apply the user's committed manual edits to the freshly
    # generated sources so they survive regeneration (blueprint stays the source
    # of truth for architecture; overlays preserve hand-tuned logic).
    if not getattr(args, "no_overlay", False):
        from src.build.overlay_stage import apply_overlays_stage

        apply_overlays_stage(workspace, enabled=True)

    # Autonomous Hardware-Polymerization: probe the host and polymorphically
    # rewrite the freshly generated sources for it, after code generation but
    # before any linking/execution.  Runs transparently with no user flags.
    if not getattr(args, "no_polymorph", False):
        _maybe_run_polymorphization(workspace)

    # Self-evolution after the initial build (feature #5).
    if not getattr(args, "no_evolution", False):
        _maybe_run_evolution(workspace)

    # Runtime feedback after the build (feature #3).
    if getattr(args, "runtime_feedback", False) or context.get("runtime", {}).get("enable_feedback"):
        _run_runtime_stage(context, workspace)

    # Validation gatekeeper (feature #5).
    return _run_validation_stage(context, workspace)

