# AeroNova

AeroNova is a deterministic, self-evolving, multi-agent build optimization and compiler orchestration engine. Rather than executing static compile-and-link steps, AeroNova models the compilation lifecycle as a multi-objective optimization problem, balancing execution speed, binary/structural density, and validation accuracy.

While standard compiler backends act as static execution paths, AeroNova integrates an active multi-agent feedback loop (the Cortex) that dynamically analyzes, mutates, and heals build parameters over successive orchestration cycles.

---

## 🧬 Key Architectural Pillars

### 1. The Cortex (Multi-Agent Decider Loop)
AeroNova utilizes a coordinated multi-agent layer to observe, guide, and adapt active workspace optimizations:
* **Accuracy Guard:** Monitors code coverage metrics, test outputs, and compiler safety floors, systematically rolling back parameter mutations that drop below safety thresholds.
* **Performance Profiler:** Measures micro-benchmarks and total wall-time across build cycles to quantify execution latencies and hardware matching classes.
* **Compactor Agent:** Assesses abstract grammar complexity, managing dead-code graph elimination depth and variable scope minification.

### 2. Universal 1D UAST and Term Rewriting System (TRS)
* **Concrete Syntax Representation:** Source documents are parsed via Tree-sitter into a lossless representation, preserving formatting, whitespace bounds, and developer trivia.
* **Linearized 1D UAST Array:** Flattened from the nested syntax tree to maximize hardware cache alignment during heavy dependency analysis.
* **Resilient Fallback Parsing Engine:** In virtual execution runtimes experiencing FFI binary or tree-sitter compilation discrepancies, the engine dynamically isolates crashes and maps source files into deterministic 1-D flat arrays via an abstract structural regex proxy. This ensures downstream semantic hashing and symbol processing complete successfully without memory violations or key faults.

### 3. Self-Healing v2 Engine (Automated Program Repair)
When a build target contains severe lexical faults, AeroNova engages an active, sandboxed program recovery pipeline rather than breaking the build toolchain:
* **Syntactic Lookahead Recovery:** Traverses the syntax tree to intercept `ERROR` and `MISSING` markers, executing in-memory token injections to establish pseudo-valid CST streams.
* **Stateful LSP Diagnostic Reflux:** Hooks into native JSON-RPC proxy sessions with active language servers (`rust-analyzer`, `pyright`, `clangd`) to capture explicit error codes and dynamically apply structural use declarations or missing imports.
* **Verification Containment Loop:** Restricts healing iterations to a temporary shadow staging area (`.aero/bootstrap_stage/`) bounded by a strict 3-retry budget. Verified files are swapped into production cleanly via thread-safe atomic calls.

### 4. Custom Feature Ingestion & Managed Target Routing
To accommodate raw, multi-language system simulations and third-party algorithmic extensions without polluting core execution environments, AeroNova includes an open target-provisioning layout:
* **Gated Language Routing:** Inspects foreign entry boundaries at the syntax level to cleanly isolate compilation logic, executing specialized compilation layers exclusively when matching source patterns are confirmed.
* **Heterogeneous Asset Binding:** Seamlessly bridges independent source monoliths—such as standalone Python simulation scripts and multi-threaded Rust backends—under a unified multi-objective Pareto evolution sweep.
* **Active In-Process Merger:** Pipelines successful out-of-tree workspace binaries straight back into the live core application tree via thread-safe runtime hot-swapping.

---

## ⚙️ Configuration Setup (`blueprint.aero`)

Build targets, compilation requirements, and context registries are explicitly defined using a block-format TOML manifest placed at the root of the workspace.

### ⚠️ Strict Formatting Constraints (Python 3.12 Compliance)
When declaring inline arrays of tables under the `[graph]` block, **do not use JSON-style colons (`:`) as key-value separators**. The native parsing toolchain (`tomllib`) enforces standard TOML layout compliance; all dictionary properties must utilize explicit equals signs (`=`).

### Example Integration Specification

```toml
[system]
name = "production-scale-polyglot-pipeline"
strategy = "universal-engine"
ephemeral_code = true

[context_registry.core_application]
path = "./src/app_logic.py"
language = "python"
preserve_original_logic = false

[scaling]
auto_split_threshold = 120       # Line count limits that trigger auto-decomposition
max_module_complexity = 12       # Maximum McCabe complexity metric allowed per function scope
hierarchy_depth = 4              # Package nesting constraints

[graph]
# Valid TOML syntax using '=' for inline array properties
targets = [{name = "core_orchestrator", source = "translator/core_orchestrator.py", output = "build_artifacts/core_orchestrator.optimized.py"}, {name = "anyon_extension", source = "translator/anyon_extension.py", output = "build_artifacts/anyon_extension.optimized.py"}]
dependencies = []
boundaries = ["core_orchestrator"]

[compiler]
toolchain = "python3"
optimization_level = "aggressive"

# ==============================================================================
# CUSTOM ADDITIONS: MANAGED EXTENSION CHANNELS
# ==============================================================================

[qg_orchestrator]
path = "/content/qg_orchestrator.py"
language = "python"
opt_level = "strict"

[sim_backend]
path = "/content/lib.rs"
language = "rust"
opt_level = "max_performance"

```

---

## 🛠️ CLI Reference Manual

AeroNova exposes a comprehensive systems command-line interface to orchestrate static builds, dependency graph visualizations, and automated repair cycles. All main execution sweeps require an explicit subcommand verb flag.

### Run Pipeline Build

Executes the full compiler pipeline, analyzing dependency graphs, evaluating caches, running parameter tuning, and executing code-generation cycles:

```bash
python main.py build

```

### Visualise Build Graph Tree

Parses `blueprint.aero`, resolves the execution DAG, checks compiler availability, and outputs a clean tree layout without mutating files:

```bash
python main.py plan

```

### Execute Complexity Analysis & Code Splitting

Evaluates function complexity and module paths against scaling thresholds. Use `--apply` to automatically split oversized functions into distinct files:

```bash
python main.py decompose --apply

```

### Target-Specific Bounded Self-Healing

Launches the rule-based, iterative self-healing repair loop directly on a single compilation target:

```bash
python main.py heal --path /path/to/module.py --max-attempts 3

```

### Out-of-Tree Scaffolding & Active Feature Integration

Generates a standalone, fully structured micro-crate distribution from a raw source entry. Passing the structural validation constraints allows you to merge the output back into active core processes:

```bash
python main.py scaffold --source-entry /path/to/source.rs --build --merge-active

```

### Commit Manual Layout Overlays

Saves manual, hand-tuned adjustments made directly to an auto-generated file as an overlay patch, ensuring human edits survive automated regeneration:

```bash
python main.py commit-overlay /path/to/generated_file.py

```

### Manage Memory Caches

Inspects data statistics or purges the memoization cache and dependency cycle maps:

```bash
python main.py cache stats
python main.py cache clear

```

---

## 📄 License

This framework is open-source software distributed under the terms of the MIT License.
