# Architectural Core: Universal Parsing, Polyglot Decomposition, and Self-Healing Staging

This document outlines the core internal components, data flows, and structural mutation pipelines that govern AeroNova. It details how the engine operates both as an out-of-tree polyglot code-splitting utility and as a resilient, self-hosting coordinate bootstrap system for multi-million-line physics simulators.

## Design Principles

1. **Backward Compatibility:** Every capability is entirely opt-in. Blueprints that omit advanced scaling blocks or physics metrics produce identical, deterministic behaviors. All 51 pre-existing baseline framework validation tests pass completely unchanged.
2. **Staging Isolation & Self-Targeting Safety:** The tool prioritizes core interpreter runtime protection. If an execution path targets an active dependency within AeroNova's own running tree, it dynamically quarantines disk writes until code structures pass an independent validation sweep.
3. **Graceful Degradation:** Heavy external operational infrastructure (such as Kubernetes backends, OpenBLAS, MPI bindings, or CUDA drivers) is safely detected at runtime and lazy-imported. If absent, the engine flags the target feature as unavailable and falls back to local execution without aborting the build.
4. **Coherent Configuration Surfaces:** The human-facing INI/TOML format (`blueprint.aero`) and the internal engine-facing JSON schema (`blueprint_config.json`) are tightly aligned. The parser strictly validates input DSL syntax and boundaries before exposing them to the orchestration context.

---

## Core Component Matrix

| Functional Area | Internal Architecture & Mechanism | Primary Target Files |
| --- | --- | --- |
| **Blueprint Parser** | Handles declarative schema validation for optional custom zones, scaling thresholds, and layout parameters. | `blueprint_parser.py` |
| **Universal Front-End** | Normalizes disparate language syntaxes (Python, Rust, C/C++, Fortran) into a 1D linearized Universal Abstract Syntax Tree (UAST) with FFI and GPU kernel edge tracking. | `src/analysis/semantic_mapper.py` |
| **Decomposition Engine** | Employs an operational Term Rewriting System (TRS) driven by S-expression token matching to split monoliths along lossless class and global function boundaries. | `builder_brains/decision_tree.py`, `builder_brains/orchestrator.py` |
| **Dependency Reflux** | Analyzes local/global symbol scopes across newly split modules; extracts duplicated configurations into a shared index and injects missing relative imports. | `builder_brains/reflux_engine.py` |
| **Shadow Bootstrapper** | Detects self-hosting operations, locks direct file-system modifications, routes active mutations to an isolated cache, and conducts an atomic swap pass. | `src/build/bootstrap_staging.py` |
| **Library Auto-Tuning** | Uses environmental probing (via pkg-config and explicit linker checks) to discover BLAS/LAPACK/MPI paths and append optimization flags to the genetic genome. | `src/build/library_tuner.py`, `src/evolution/bootstrap.py` |
| **Precision Shield** | Computes per-compiler strict floating-point flag configurations (GCC/Clang, Intel, rustc, nvcc) to block unsafe code-generation optimizations. | `src/precision_shield/shield.py` |
| **Distributed builds** | Operates a coordination pipeline supporting local, SSH, and Kubernetes worker pools backed by a shared network cache interface. | `src/build/distributed.py`, `src/evolution/sandbox_manager.py` |
| **Dimensional Analyzer** | Executes heuristic dimensional unit analysis over project syntax layers via a lightweight custom AST visitor without CAS runtime overhead. | `src/physics/units.py` |

---

## Complete System Data Flow

```
 blueprint.aero (INI/DSL) ──┐
                            ├─ parser & validation ──► Context Registry
 blueprint_config.json ─────┘                              │
                                                           ▼
                                                    SemanticMapper
                                            (Lossless CST Translation)
                                                           │
                                                           ▼
                                              Linearized 1D UAST Array
                                                           │
                                 ┌─────────────────────────┴─────────────────────────┐
                                 ▼                                                   ▼
                    [If auto_split thresholds hit]                       [Parallel Target Compilation]
                     Term Rewriting System (TRS)                          ├── LibraryTuner (Linker Flags)
                                 │                                        ├── PrecisionShield (FP Enforcements)
                                 ▼                                        ├── GPUPipeline (CUDA/HIP Kernels)
                    Isolate Shadow Staging Area                           └── DistributedCoordinator
                     (.aero/bootstrap_stage/)                                  (Local / SSH / K8s Pools)
                                 │
                                 ▼
                     Symbol Scope Reflux Engine
                     (Import Injection & utils.py)
                                 │
                                 ▼
                     Atomic Change-Swap Deployment

```

---

## Testing Framework & Verification Metrics

AeroNova runs a highly comprehensive testing suite consisting of **117 passing automated verification tests**. The test architecture evaluates runtime performance regressions and structural accuracy guarantees across three primary criteria:

* **Structural Integrity & Self-Healing:** Validates that the Term Rewriting System can safely process, decompose, and reconnect code networks without throwing compilation syntax drops, NameErrors, or losing manual developer patch overlays.
* **Numerical & Mathematical Invariants:** Verifies strict-FP reproducibility rules (e.g., ensuring a mock simulator cleanly computes $\pi$ to double precision) and checks that the Precision Shield successfully blocks dangerous optimization constant-folding paths.
* **Scale & Distributed Bounds:** Tracks single-machine vs. cluster execution time differentials, records cache hit-rates after modular code sharding, and profiles underlying host hardware vector capability classes.

---

## Deliberate Architectural Trade-offs

* **Staging I/O Overhead over Raw Speed:** When self-hosting paths are triggered, the engine purposefully trades write latency for system safety. Forcing every structural change through a shadow cache folder, parsing it, and verifying it via the internal scanner before executing an atomic swap introduces execution overhead, but it guarantees that a faulty code mutation pass can never leave AeroNova in a permanently corrupted or bricked state.
* **Pragmatic Heuristics over Absolute Type Environments:** FFI border detection, text n-gram matching, and dimensional unit analysis operate as highly performant semantic heuristics. They are engineered to catch obvious compilation bugs and spatial errors across multiple languages without imposing the massive, slow computational overhead of an exact mathematical type-system checker.
* **Lazy Dependency Loading for Core Lightness:** While distributed remote management packages like `fabric` or `kubernetes` are pinned in the global installation manifest, they are isolated behind lazy-import wrappers. They load into the active process memory pool only when a user explicitly declares a distributed strategy backend in their blueprint, keeping local single-machine builds completely dependency-free.
* **Simulated Evolutionary Core Cost Modeling:** The multi-objective reinforcement learning Pareto optimization engine models compilation profiles and library footprint effects using structural metadata arrays rather than launching thousands of expensive real-world physical compiler processes inside the localized search loop, leaving the heavy lifting to dedicated downstream compilation workers.
