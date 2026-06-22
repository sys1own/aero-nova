# AeroNova

**The Living Blueprint Engine — Build, Evolve, and Preserve**

AeroNova is a next‑generation build tool that treats your **blueprint** as the single, persistent source of truth for your entire system. The code is ephemeral — the blueprint is permanent.

---

## What AeroNova Does (Today)

AeroNova takes any source code across **any programming language autonomously**, plus optional unstructured text (`.md`, `.txt`, `.pdf`), and automatically transforms it into a **production‑ready, modular, optimised repository** — while letting you **preserve manual edits** across automated code regenerations.

By ditching language-specific compilers and non-deterministic probabilistic models, AeroNova uses formal grammar logic and universal syntax mappings to manage polyglot systems with zero-dependency runtime precision.

### Core Capabilities (All Implemented)

| Feature | Description |
| --- | --- |
| **Blueprint‑driven builds** | Declarative config (`blueprint.aero`) under 10 lines; infers DAG, dependencies, and boundaries.

 |
| **Universal Parsing Front-End** | Utilizes Tree-sitter to ingest raw source code into a lossless Concrete Syntax Tree (CST), retaining all token and layout data. |
| **UAST Normalization** | Translates disparate language syntaxes into a unified 4-layer Universal Abstract Syntax Tree ($\Psi: \mathbf{T}_L \rightarrow \mathbf{U}$). |
| **Polyglot Decomposition** | Employs a declarative Term Rewriting System (TRS) to analyze metrics and split monoliths across any syntax via S-expression query matching. |
| **Deterministic Self-Healing** | Intercepts structured compiler JSON diagnostics and mirrors language states with an internal stateful LSP proxy to fix errors algorithmically. |
| **Two-Tiered Structural Merging** | Merges manual edits safely using coarse-grained semantic identity matching and fine-grained Parent-Child-Successor (PCS) tree triple alignments. |
| **Hardware Profiling** | Probes cache, cores, and SIMD registers (AVX‑512, ARM NEON) for hardware-specific structural optimizations.

 |
| **Structural Memoisation** | Caches builds by structural UAST configuration rather than file text hashes (whitespace or comments never trigger rebuilds).

 |

---

### The Ingestion & Normalization Pipeline

AeroNova normalizes all incoming code formats into a single intermediate schema before mapping relationships to the DAG:

* **Metadata Block:** Evaluates file metrics, byte spans, and syntax volumes for total build tracking.
* **Flat Node Array:** Serializes deep tree hierarchies into a linearized 1D node collection to eliminate recursive traversal performance overhead.
* **Node Taxonomy & Alignment:** Maps syntax constructs directly to generic definitions (e.g., matching Rust’s `pub fn`, Python’s `def`, and COBOL’s `METHOD-ID.` into a uniform functional block framework).

---

### Living Blueprint DSL

The `blueprint.aero` file orchestrates system scaling and contextual boundaries without changing backend scripts:

```toml
[system]
name = "my-system"
strategy = "universal-engine"     # Powered by declarative grammar matching
ephemeral_code = true             # Code is regenerated; manual patches are stored as structural overlays

[context_registry]
  [context_registry.payroll]
  path = "./legacy/payroll.cob"
  language = "cobol"              # Autonomously mapped via universal tree nodes
  preserve_original_logic = true

[scaling]
  auto_split_threshold = 1500     # Lines before auto-decomposition
  max_module_complexity = 200     # Evaluated via structural branching node density
  hierarchy_depth = 4

```

---

### Deterministic Polyglot Self-Healing

AeroNova wraps your host environment toolchains to catch errors and execute automated repair sequences. When a build failure occurs, the engine handles the anomaly using formal transformation tracking:

$$H(\text{CST}_{\text{orig}}, e) \to \text{CST}_{\text{healed}} \quad \text{where} \quad \text{CST}_{\text{healed}} = \text{Replace}(P(e, \text{CST}_{\text{orig}}), R(e))$$

* **Host Environment Introspection:** Automatically probes system binary paths and environment registries (`CC`, `CXX`, etc.) to locate and check local compilation capabilities using isolated test targets.
* **Stateful LSP Synchronization:** Spawns background JSON-RPC proxy sessions with native language servers (`clangd`, `rust-analyzer`, `pyright`) to intercept real-time diagnostic packages.
* **Diagnostic Correction Matrix:** Maps explicit error codes (e.g., missing block terminators, invalid mutability states, or unlinked module targets) directly to structural rewrite steps, capped at an iterative budget of 3 builds before rolling back safely to protect system invariants.

---

### Two-Tiered Overlay System (Preservation Engine)

Manual modifications to automatically generated source code are isolated and protected against future builds without brittle, line-based text diff tools:

1. **Semantic Entity Merging:** Isolates file changes at a high construct level (namespaces, scopes, imports) using a calculated structural signature:

$$\text{ID} = (\text{Scope}_{\text{namespace}}, \, \text{Type}_{\text{construct}}, \, \text{Name}_{\text{entity}})$$


2. **Fine-Grained PCS Triple Merging:** If structural collisions occur within the same entity block, AeroNova breaks the changes down into Parent-Child-Successor relationships, tracks similarity via bottom-up node density propagation, and aligns the code trees while recovering original layout formatting.

---

## CLI Commands (All Active)

| Command | Purpose |
| --- | --- |
| `build` | Generate, compile, and execute the self-healing toolchain loop.

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

* **Python 3.10+**
* **Tree-sitter Runtime Binaries**
* **Local Language Compilers/LSPs** mapped within your host environment paths (`clangd`, `rust-analyzer`, etc.)

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
Verified, Production-Ready Modular Architecture

```

---

**AeroNova — The blueprint is the system. Everything else is detail.**

---

Would you like to adjust the Quick Start code blocks in this updated README to showcase how a developer sets up a new language configuration (like COBOL or Zig) using the updated CLI pipeline?
