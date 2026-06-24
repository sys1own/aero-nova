from __future__ import annotations
"""Auto-decomposed from monolith: function create_parser."""


import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

import orchestrator



from .main_analyze_command import analyze_command
from .main_build_command import build_command
from .main_cache_command import cache_command
from .main_check_command import check_command
from .main_commit_overlay_command import commit_overlay_command
from .main_decompose_command import decompose_command
from .main_heal_command import heal_command
from .main_infer_command import infer_command
from .main_ingest_command import ingest_command
from .main_invariants_command import invariants_command
from .main_libraries_command import libraries_command
from .main_plan_command import plan_command
from .main_polymorphize_command import polymorphize_command
from .main_profile_command import profile_command
from .main_runtime_command import runtime_command
from .main_scaffold_command import scaffold_command
from .main_shield_command import shield_command
from .main_toolchain_command import toolchain_command
from .main_validate_command import validate_command
def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aero Multi-Tool: next-generation build orchestration CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- build (original) ---
    build_parser = subparsers.add_parser("build", help="Run the full builder pipeline")
    build_parser.add_argument("--workspace", default=".", help="Workspace root to build")
    build_parser.add_argument(
        "--blueprint",
        default=None,
        help="Path to blueprint.aero (default: <workspace>/blueprint.aero)",
    )
    build_parser.add_argument("--cycles", type=int, default=3, help="Number of orchestration cycles")
    build_parser.add_argument(
        "--telemetry-interval",
        type=float,
        default=2.0,
        help="Seconds between telemetry refreshes",
    )
    build_parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    build_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print the synthesised manifest, exact cargo command + env (RUSTFLAGS), and detected deps",
    )
    build_parser.add_argument("--no-hpc", action="store_true", help="Force a local build, ignoring [hpc] settings")
    build_parser.add_argument("--no-evolution", action="store_true", help="Skip the self-evolution pass after building")
    build_parser.add_argument("--no-hardware-probe", action="store_true", help="Skip hardware profiling at build start")
    build_parser.add_argument("--no-polymorph", action="store_true", help="Skip autonomous hardware-polymerization of generated code")
    build_parser.add_argument("--no-overlay", action="store_true", help="Skip re-applying committed user overlays to generated code")
    build_parser.add_argument("--runtime-feedback", action="store_true", help="Run the runtime benchmark after building")
    build_parser.add_argument("--validation-only", action="store_true", help="Skip the build; only run the validation suite")
    build_parser.add_argument(
        "--bootstrap-active",
        action="store_true",
        help="Signal that this invocation is a nested bootstrap pass (prevents infinite recursion)",
    )
    build_parser.add_argument(
        "--no-scaffold-build",
        action="store_true",
        help="When [scaffold] is active, synthesize the repo but skip cargo build",
    )
    build_parser.set_defaults(handler=build_command)

    # --- plan (discover, validate, build DAG, print visual tree) ---
    plan_parser = subparsers.add_parser(
        "plan",
        help="Parse blueprint.aero, resolve the build DAG, and print a visual tree",
    )
    plan_parser.add_argument("--workspace", default=".", help="Workspace root containing blueprint.aero")
    plan_parser.add_argument("--blueprint", default=None, help="Explicit path to a blueprint file")
    plan_parser.set_defaults(handler=plan_command)

    # --- check (strict blueprint validation, no build) ---
    check_parser = subparsers.add_parser(
        "check", help="Strictly validate a block-format blueprint.aero (no build)"
    )
    check_parser.add_argument("--workspace", default=".", help="Workspace root containing blueprint.aero")
    check_parser.add_argument("--blueprint", default=None, help="Explicit path to a blueprint file")
    check_parser.set_defaults(handler=check_command)

    # --- analyze ---
    analyze_parser = subparsers.add_parser("analyze", help="Run semantic proximity mapping")
    analyze_parser.add_argument("--workspace", default=".", help="Project root")
    analyze_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    analyze_parser.add_argument("--export", default=None, help="Export UAST graph to JSON file")
    analyze_parser.set_defaults(handler=analyze_command)

    # --- shield ---
    shield_parser = subparsers.add_parser("shield", help="Run precision shield validation")
    shield_parser.add_argument("--workspace", default=".", help="Project root")
    shield_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    shield_parser.set_defaults(handler=shield_command)

    # --- profile ---
    profile_parser = subparsers.add_parser("profile", help="Run hardware profiling")
    profile_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    profile_parser.set_defaults(handler=profile_command)

    # --- cache ---
    cache_parser = subparsers.add_parser("cache", help="Manage the memoization cache")
    cache_parser.add_argument("action", choices=["stats", "clear", "cycles"], help="Cache action")
    cache_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    cache_parser.set_defaults(handler=cache_command)

    # --- libraries ---
    lib_parser = subparsers.add_parser("libraries", help="Probe numerical libraries and emit flags")
    lib_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    lib_parser.set_defaults(handler=libraries_command)


    # --- ingest ---
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest source into the AST registry (--path) or external trees ([context])",
    )
    ingest_parser.add_argument("--workspace", default=".", help="Workspace root to ingest into")
    ingest_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    ingest_parser.add_argument(
        "--path",
        default=None,
        help="File or directory to ingest into the AST registry and [context_registry]",
    )
    ingest_parser.add_argument(
        "--context-name",
        dest="context_name",
        default=None,
        help="Name for the context (defaults to the target directory name)",
    )
    ingest_parser.add_argument(
        "--language",
        default=None,
        choices=["python", "rust", "cpp", "c", "fortran", "cobol"],
        help="Force a language (otherwise inferred from file extensions)",
    )
    ingest_parser.add_argument(
        "--blueprint",
        default=None,
        help="Path to blueprint.aero to register the context in (default: <workspace>/blueprint.aero)",
    )
    ingest_parser.add_argument(
        "--db",
        default=None,
        help="Path to the AST registry database (default: <workspace>/.aero/registry.db)",
    )
    ingest_parser.add_argument(
        "--list",
        action="store_true",
        help="List all ingested contexts in the AST registry with their semantic hashes",
    )
    ingest_parser.set_defaults(handler=ingest_command)

    # --- commit-overlay ---
    overlay_parser = subparsers.add_parser(
        "commit-overlay",
        help="Save manual edits to a generated file as an overlay patch (preserved across rebuilds)",
    )
    overlay_parser.add_argument("file", help="Path to the edited generated file")
    overlay_parser.add_argument("--workspace", default=".", help="Workspace root")
    overlay_parser.set_defaults(handler=commit_overlay_command)

    # --- invariants (semantic fluidity) ---
    invariants_parser = subparsers.add_parser(
        "invariants", help="Ingest unstructured context + code into the Invariant Schema"
    )
    invariants_parser.add_argument("--source-dir", required=True, help="Directory of mixed context files to ingest")
    invariants_parser.add_argument("--workspace", default=".", help="Workspace root (used to resolve the default report path)")
    invariants_parser.add_argument("--output", default=None, help="Explicit path for the invariant_schema_report.json")
    invariants_parser.set_defaults(handler=invariants_command)

    # --- infer (invisible configuration layer) ---
    infer_parser = subparsers.add_parser(
        "infer", help="Infer the full execution DAG from an ultra-lean blueprint"
    )
    infer_parser.add_argument("--workspace", default=".", help="Workspace root containing blueprint.aero")
    infer_parser.add_argument("--blueprint", default=None, help="Explicit path to a lean blueprint file")
    infer_parser.add_argument("--json", action="store_true", help="Emit the inferred DAG as JSON")
    infer_parser.set_defaults(handler=infer_command)

    # --- decompose (deterministic dependency/complexity evaluator) ---
    decompose_parser = subparsers.add_parser(
        "decompose",
        help="Analyse imports/complexity, write the DAG to blueprint.aero, and optionally auto-split functions",
    )
    decompose_parser.add_argument("--workspace", default=".", help="Workspace root")
    decompose_parser.add_argument("--path", default=None, help="Single file to analyse (default: whole workspace)")
    decompose_parser.add_argument("--blueprint", default=None, help="Path to blueprint.aero (default: <workspace>/blueprint.aero)")
    decompose_parser.add_argument("--apply", action="store_true", help="Perform decomposition (default: dry-run plan only)")
    decompose_parser.add_argument("--no-dag", action="store_true", help="Do not write the inferred DAG to blueprint.aero")
    decompose_parser.set_defaults(handler=decompose_command)

    # --- toolchain (host environment discovery) ---
    toolchain_parser = subparsers.add_parser(
        "toolchain",
        help="Discover, validate, and cache host compilers/linkers/runtimes",
    )
    toolchain_parser.add_argument("--workspace", default=".", help="Workspace root")
    toolchain_parser.add_argument("--blueprint", default=None, help="Path to blueprint.aero (drives language set)")
    toolchain_parser.add_argument(
        "--language",
        default=None,
        choices=["c", "cpp", "rust", "fortran", "python"],
        help="Probe only this language (default: languages from the context registry)",
    )
    toolchain_parser.add_argument("--no-validate", action="store_true", help="Skip the sanity-compile validation step")
    toolchain_parser.set_defaults(handler=toolchain_command)

    # --- heal (deterministic self-healing build loop) ---
    heal_parser = subparsers.add_parser(
        "heal",
        help="Run the bounded, rule-based self-healing build loop on a module",
    )
    heal_parser.add_argument("--path", required=True, help="Source module to build and heal")
    heal_parser.add_argument("--workspace", default=".", help="Workspace root")
    heal_parser.add_argument("--blueprint", default=None, help="Path to blueprint.aero (failures are flagged here)")
    heal_parser.add_argument("--language", default=None, choices=["rust", "c", "cpp"], help="Force the language")
    heal_parser.add_argument("--max-attempts", type=int, default=3, help="Build attempt budget (default 3)")
    heal_parser.set_defaults(handler=heal_command)

    # --- polymorphize (autonomous hardware-polymerization) ---
    poly_parser = subparsers.add_parser(
        "polymorphize", help="Inspect the host and polymorphically rewrite generated code for it"
    )
    poly_parser.add_argument("--source-dir", default="build_artifacts", help="Directory of generated code to rewrite")
    poly_parser.add_argument(
        "--cache-dir", default=str(Path(".aero") / "polymorph_cache"), help="Ephemeral output cache directory"
    )
    poly_parser.add_argument("--profile-only", action="store_true", help="Only print the host topology; do not rewrite")
    poly_parser.set_defaults(handler=polymorphize_command)

    # --- validate ---
    validate_parser = subparsers.add_parser("validate", help="Run the validation suite")
    validate_parser.add_argument("--workspace", default=".", help="Project root")
    validate_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    validate_parser.set_defaults(handler=validate_command)

    # --- runtime ---
    runtime_parser = subparsers.add_parser("runtime", help="Run the runtime benchmark")
    runtime_parser.add_argument("--workspace", default=".", help="Project root")
    runtime_parser.add_argument("--config", default=None, help="Path to blueprint_config.json")
    runtime_parser.set_defaults(handler=runtime_command)

    # --- scaffold (out-of-tree standalone repo generator) ---
    scaffold_parser = subparsers.add_parser(
        "scaffold", help="Generate a turn-key standalone repo from a source file (out-of-tree)"
    )
    scaffold_parser.add_argument(
        "--source-entry", required=True,
        help="Path to the source file, from anywhere (e.g. /content/lib.rs, ../data/core.rs)",
    )
    scaffold_parser.add_argument("--name", default=None, help="Crate/repo name (default: inferred from the file)")
    scaffold_parser.add_argument(
        "--distribution-directory", default=None,
        help="Where to write the repo (default: a temp dir outside the tool tree)",
    )
    scaffold_parser.add_argument(
        "--dep", action="append", default=None,
        help="Override/add a dependency: --dep rug=1.24 (repeatable)",
    )
    scaffold_parser.add_argument("--build", action="store_true", help="Also compile the repo via cargo (with recovery)")
    scaffold_parser.add_argument(
        "--merge-active", action="store_true",
        help="After a successful --build, copy the compiled .so/.dylib into AeroNova's "
             "live core/extensions/ layer and load it so the component is instantly importable",
    )
    scaffold_parser.add_argument("--no-keep", action="store_true", help="Delete the temp workspace afterwards")
    scaffold_parser.add_argument("--verbose", action="store_true", help="Print each scaffolding step")
    scaffold_parser.set_defaults(handler=scaffold_command)

    return parser

