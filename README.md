# AeroNova

AeroNova is an ultra-scale, high-performance polyglot build orchestration and automated code-splitting engine. Designed to parse, validate, and optimize intricate, tightly coupled micro-services and monolithic codebases, AeroNova handles the heavy lifting of codebase restructuring, dependency reflux mapping, and resilience-driven optimization passes.

---

## 🧬 Core Architecture

AeroNova decouples syntax from language quirks by processing source code through three interconnected layers:

1. **Lossless Concrete Syntax Tree (CST):** Native source documents are ingested via Tree-sitter parsers to establish immutable structural geometries, preserving formatting bounds, comments, and whitespace invariants.
2. **1D Linearized UAST Array:** The nested CST is flattened into a highly scannable, contiguous 1D Universal Abstract Syntax Tree array to maximize CPU cache locality during intense graph queries.
3. **Declarative Term Rewriting System (TRS):** Code transformations, structural partitioning, and module splitting are governed by a algebraic rewrite loop that maps matching pattern matrices to target code targets safely.

---

## ⚡ Self-Healing v2 Engine

AeroNova features a resilient, multi-step **Automated Program Repair (APR)** pipeline. Instead of failing the build when encountering syntax mutations or missing context frames, the compiler engages an active three-tier recovery runtime:


```

```
[Malformed Source Asset] ───► [Syntactic Lookahead Recovery]
                                          │ (In-Memory Patching)
                                          ▼
[Atomic Sandbox Swap]    ◄─── [Sandboxed Staging Loop] (B=3)
      (Promoted)                          ▲
                                          │ (TRS Reflux Injections)
                              [Stateful LSP Diagnostic Binder]

```

```

### 1. Syntactic Lookahead Recovery
The front-end scanner captures Tree-sitter `ERROR` and `MISSING` nodes in real time. Rather than halting execution, it computes a local search context and dynamically injects temporary structural tokens (such as missing block colons, trailing statements, or unclosed scope braces) to reconstruct a pseudo-valid CST stream in-memory.

### 2. Stateful LSP Diagnostic Binding
AeroNova hooks into background JSON-RPC proxy sessions with active Language Servers (`pyright`, `rust-analyzer`, `clangd`). Diagnostic errors are caught, parsed, and translated by the engine into deterministic TRS commands:
* **`reportUndefinedVariable`** $\to$ Automatic lookup and binding of unresolved local symbol tokens.
* **`reportMissingImports`** $\to$ Generation of missing absolute module framework references.
* **`E0433 / E0405`** $\to$ Direct lookup and injection of missing Rust trait scopes and usage declarations.

### 3. Sandboxed Staging & Verification Bounded Loop
To ensure unverified modifications never pollute production files, all healing routines are isolated within a staging area located at `.aero/bootstrap_stage/`. 

Let $W$ represent the production workspace directory and $S_w \subset W$ represent the set of malformed files targeted for repair. The shadow staging directory is defined as $C = \text{".aero/bootstrap_stage/"}$. For a target file $f \in S_w$, the isolation mapping $M$ duplicates the original source file into the staging workspace:

$$f_c = M(f), \quad \text{where } \text{Path}(f_c) = C \mathbin{\Vert} \text{RelativePath}(f)$$

Let $V(f_c) \in \{0, 1\}$ represent the compile-time validation function. This function executes compilation scripts and returns $1$ if the build succeeds without warnings or errors, and $0$ otherwise. Let $\mathcal{R}$ represent the set of syntactic and semantic repair operations. Each repair iteration $i$ applies a selected transformation $R_i \in \mathcal{R}$ to the staged file:

$$f_c^{(i)} = R_i\left(f_c^{(i-1)}\right)$$

The containment loop operates within a strict execution budget $B \in \mathbb{N}$ (capped at 3 retries). The transactional state machine strictly follows this logic:

$$\text{State}(i) = \begin{cases} 
\text{Swap}(f_c^{(i)}, f), & \text{if } V\left(f_c^{(i)}\right) = 1 \\
\text{Loop}(i+1), & \text{if } V\left(f_c^{(i)}\right) = 0 \text{ and } i < B \\
\text{Purge}(f_c) \land \text{Abort}, & \text{if } V\left(f_c^{(i)}\right) = 0 \text{ and } i = B 
\end{cases}$$

If validation fails on every attempt within the budget, the transaction is safely rolled back, the staging layout is purged, and a fallback status is logged without altering your code assets.

---

## 🎨 Two-Tiered Structural Merging

To guarantee that automated machine mutations never discard human formatting choices or documentation layout comments, the generator leverages a two-tier compaction alignment strategy:

* **Tier 1: Semantic Entity Alignment:** Modifies structural fragments strictly by validating identity hashes ($\text{Hash}(\text{Type} \parallel \text{Name} \parallel \text{Scope})$). Unchanged functions, classes, and variable signatures are left fully untouched, locking in original code style structures.
* **Tier 2: Parent-Child-Sibling (PCS) Trivia Alignment:** Extracts layout comments and formatting markers (trivia) from the original file stream, relative positions them to local AST nodes, and re-anchors them back cleanly above the newly repaired target entities.

---

## ⚙️ Configuration Setup (`blueprint.aero`)

Build layouts are defined using a declarative blueprint configuration file located at the root of your target workspace:

```toml
[system]
name = "production-cluster-pipeline"
strategy = "universal-engine"
ephemeral_code = true

[context_registry]
  [context_registry.core_application]
  path = "./src/app_logic.py"
  language = "python"
  preserve_original_logic = false

[scaling]
  auto_split_threshold = 120       # Triggers splitting if node count token limits are breached
  max_module_complexity = 12       # Forces structure decomposition rules on high branching metrics
  hierarchy_depth = 4              # Determines directory tree nesting depth constraints

[graph]
dependencies = []
boundaries = ["core_application"]
targets = ["core_application"]

[compiler]
toolchain = "python3"
optimization_level = "aggressive"

```

---

## 🚀 Usage Guide

To execute a clean build and partition pass over an active target workspace, run the engine CLI interface:

```bash
python main.py build --workspace /path/to/your/target_sandbox

```

### Pipeline Diagnostics Index

When a build run completes, check the generated metrics report for diagnostic status signals:

| Status Code | Subsystem Meaning | Safety Outcome |
| --- | --- | --- |
| `noop` | Target source contains 0 errors; no healing rules required. | File left pristine. |
| `promoted` | Syntax or semantic errors discovered, completely fixed, and verified. | File atomically updated. |
| `rolled_back` | Staged code modification attempts failed compilation check validation rules. | Staging wiped; file unchanged. |
| `fallback_unrecoverable` | Severe parser syntax errors block tree construction even after lookahead repairs. | Safe exit; file unchanged. |

---

## 📄 License

AeroNova is open-source software licensed under the MIT License.

```

```
