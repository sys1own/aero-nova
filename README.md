# AeroNova

**The Living Blueprint Engine — Build, Evolve, and Preserve**

AeroNova is a next‑generation build tool that treats your **blueprint** as the single, persistent source of truth for your entire system. The code is ephemeral — the blueprint is permanent.

---

## What AeroNova Does

AeroNova takes any source code across **any programming language autonomously**, plus optional unstructured text (`.md`, `.txt`, `.pdf`), and automatically transforms it into a **production‑ready, modular, optimised repository** — while letting you **preserve manual edits** across automated code regenerations.

By abandoning language-specific compilers and non-deterministic probabilistic models, AeroNova uses formal grammar logic and universal syntax mappings to manage polyglot systems with zero-dependency runtime precision.

### Core Capabilities

| Feature | Description |
| --- | --- |
| **Blueprint‑driven builds** | Declarative config under 10 lines; automatically infers DAG, dependencies, and boundaries.

 |
| **Universal Parsing Front-End** | Ingests raw source code into a lossless Concrete Syntax Tree (CST) using Tree-sitter, retaining all layout data.

 |
| **UAST Normalization** | Translates disparate language syntaxes into a unified 4-layer Universal Abstract Syntax Tree ($\Psi: \mathbf{T}_L \rightarrow \mathbf{U}$).

 |
| **Polyglot Decomposition** | Employs an operational Term Rewriting System (TRS) to split monoliths across any syntax via S-expression query matching.

 |
| **Self-Healing Import Reflux** | Autonomously detects missing cross-module symbols and duplicates, extracting shared utilities and injecting missing relative imports into generated sub-modules. |
| **Deterministic Self-Healing** | Intercepts compiler JSON diagnostics and mirrors language states with an internal LSP proxy to fix errors algorithmically.

 |
| **Two-Tiered Structural Merging** | Merges manual edits safely using coarse-grained semantic identity matching and fine-grained Parent-Child-Successor (PCS) tree triple alignments.

 |
| **Hardware Profiling** | Probes cache, cores, and SIMD registers (AVX‑512, ARM NEON) for hardware-specific structural optimizations.

 |
| **Structural Memoisation** | Caches builds by structural UAST configuration rather than file text hashes (whitespace or comments never trigger rebuilds).
 |

---

## The Ingestion & Normalization Pipeline

AeroNova normalizes all incoming code formats into a single intermediate schema before mapping relationships to the directed acyclic graph (DAG):

* **Metadata Block:** Evaluates file metrics, byte spans, and syntax volumes for total build tracking.


* **Flat Node Array:** Serializes deep tree hierarchies into a linearized 1D node collection to eliminate recursive traversal performance overhead.


* **Node Taxonomy & Alignment:** Maps syntax constructs directly to generic definitions (e.g., matching Rust’s `pub fn`, Python’s `def`, and COBOL’s `METHOD-ID.` into a uniform functional block framework).



---

## Advanced Polyglot Decomposition & Self-Healing Import Reflux

When system scale or structural branching node density surpasses the thresholds specified in your `blueprint.aero` file, the engine engages the **Polyglot Decomposition Pipeline**. Rather than generating static text-slices, AeroNova executes a two-phase structural mutation on your codebase:

### 1. Lossless Functional Decoupling

The engine walks the linearized 1D node map of a monolithic file, detects major structural boundaries (such as top-level classes or large functions), and cleanly breaks them out into individual standalone modules under a dedicated `decomposed/` sandbox directory. A comprehensive forwarder layer (`__init__.py`) is generated automatically to preserve the external API perimeter layout.

### 2. Autonomous Dependency Reflux

To prevent scoping anomalies, missing references, or redundant helper duplication across newly split leaf nodes, the engine executes a post-processing reflux pass:

* **Utility Consolidation:** If duplicate helper configurations or shared utility layouts are found in separate decoupled branches, they are extracted and consolidated into a unified `utils.py` module.
* **Symbol Extraction & Injection:** The engine analyzes global and local token scopes. If an isolated module invokes a token signature not natively defined within its file boundary, AeroNova tracks down the target symbol and dynamically injects the appropriate relative import statement at the top of the file.

The entire loop hooks into a post-execution validation pass, continuously verifying layout integrity until zero code-structure anomalies remain.

---

## Living Blueprint DSL

The `blueprint.aero` file utilizes standard native array notation to orchestrate system scaling, toolchains, and contextual boundaries without changing backend scripts:

```toml
[system]
name = "my-system"
strategy = "universal-engine"     # Powered by declarative grammar matching
ephemeral_code = true             # Code is regenerated; manual patches are stored as structural overlays

[context_registry]
  [context_registry.core_logic]
  path = "./main.py"
  language = "python"              # Autonomously mapped via universal tree nodes
  preserve_original_logic = false # Set to false to allow automated decomposition/splitting

[scaling]
  auto_split_threshold = 400      # Lines before triggering Term Rewriting System decomposition
  max_module_complexity = 30      # Forces optimization loops if branching node density is exceeded
  hierarchy_depth = 5

[graph]
dependencies = []
boundaries = ["core_logic"]
targets = ["core_logic"]          # Tracked as a native validation list

[compiler]
toolchain = "python3"
optimization_level = "aggressive" # Configures optimization profiling rules

[cortex]
exploration_epsilon = 0.150000    # Bounds reinforcement learning config paths
learning_rate = 0.00005

```

---

## Deterministic Polyglot Self-Healing

AeroNova wraps your host environment toolchains to catch errors and execute automated repair sequences. When a build failure occurs, the engine handles the anomaly using formal transformation tracking:

$$H(\text{CST}_{\text{orig}}, e) \to \text{CST}_{\text{healed}} \quad \text{where} \quad \text{CST}_{\text{healed}} = \text{Replace}(P(e, \text{CST}_{\text{orig}}), R(e))$$

* **Host Environment Introspection:** Automatically probes system binary paths and environment registries (`CC`, `CXX`, etc.) to locate and check local compilation capabilities using isolated test targets.


* **Stateful LSP Synchronization:** Spawns background JSON-RPC proxy sessions with native language servers (`clangd`, `rust-analyzer`, `pyright`) to intercept real-time diagnostic packages.


* **Diagnostic Correction Matrix:** Maps explicit error codes directly to structural rewrite steps, capped at an iterative budget of 3 builds before rolling back safely to protect system invariants.



---

## Two-Tiered Overlay System (Preservation Engine)

Manual modifications to automatically generated source code are isolated and protected against future builds without brittle, line-based text diff tools:

1. 
**Semantic Entity Merging:** Isolates file changes at a high construct level (namespaces, scopes, imports) using a calculated structural signature:



$$\text{ID} = (\text{Scope}_{\text{namespace}}, \, \text{Type}_{\text{construct}}, \, \text{Name}_{\text{entity}})$$

2. 
**Fine-Grained PCS Triple Merging:** If structural collisions occur within the same entity block, AeroNova breaks the changes down into Parent-Child-Successor relationships, tracks similarity via bottom-up node density propagation, and aligns the code trees while recovering original layout formatting.



---

## CLI Commands

AeroNova exposes an interactive multi-tool suite to drive the verification loop:

| Command | Purpose |
| --- | --- |
| `build` | Generate code assets, compute the multi-objective Pareto cortex, and execute the self-healing toolchain loop.

 |
| `check` | Validate blueprint semantics and check tree configurations without compilation.

 |
| `infer` | Execute Tree-sitter queries to extract paths and map global system dependencies.

 |
| `ingest` | Parse code layouts directly into the immutable structural database.

 |
| `commit-overlay` | Run structural 3-way AST matching to seal manual edits into overlays.

 |
| `validate` | Run the validation suite inside an isolated verification sandbox.

 |
| `profile` | Display local hardware cache maps and vector optimization topologies.

 |

---

## System Requirements

* 
**Python 3.10+** 


* 
**Tree-sitter Runtime Binaries** 


* 
**Local Language Compilers/LSPs** mapped within your host environment paths (`clangd`, `rust-analyzer`, etc.) 



---

## Architecture Overview

```
blueprint.aero (Living DSL)
        │
        ▼
Tree-sitter Universal Parsing (CST Generation)
        │
        ├── UAST Serialization & Taxonomy Mapping
        ├── Declarative Term Rewriting System (TRS)
        └── Stateful LSP Diagnostics / JSON Error Interception
        │
        ▼
Two-Tiered Structural Merger (Semantic Entity & PCS Alignment)
        │
        ▼
Host Toolchain Introspection & Compilation Execution
        │
        ▼
Autonomous Dependency Reflux (Import Extraction & Optimization)
        │
        ▼
Verified, Production-Ready Modular Architecture

```

---

AeroNova — The blueprint is the system. Everything else is detail.
