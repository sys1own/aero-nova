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
* **Declarative Rewriting Passes:** Manages function-level decomposition, structural splitting, and cross-boundary dependency reflux via an algebraic term rewriting system.

### 3. Self-Healing v2 Engine (Automated Program Repair)
When a build target contains severe lexical faults, AeroNova engages an active, sandboxed program recovery pipeline rather than breaking the build toolchain:
* **Syntactic Lookahead Recovery:** Traverses the syntax tree to intercept `ERROR` and `MISSING` markers, executing in-memory token injections to establish pseudo-valid CST streams.
* **Stateful LSP Diagnostic Reflux:** Hooks into native JSON-RPC proxy sessions with active language servers (`rust-analyzer`, `pyright`, `clangd`) to capture explicit error codes and dynamically apply structural use declarations or missing imports.
* **Verification Containment Loop:** Restricts healing iterations to a temporary shadow staging area (`.aero/bootstrap_stage/`) bounded by a strict 3-retry budget. Verified files are swapped into production cleanly via thread-safe atomic calls.

### 4. Dynamic Feature Scaffolding & Operational In-Tree Merging
To accommodate raw, multi-language extensions without polluting core runtime spaces, AeroNova includes an automated target-provisioning workspace engine:
* **Gated Language Routing:** Inspects foreign entry boundaries at the syntax level to cleanly isolate compilation logic, executing specialized compilation layers exclusively when matching source patterns are confirmed.
* **Macro-Aware AST Expansion:** Dynamically modifies downstream macro block structures, resolving structural namespace constraints, dependency declarations, and import scopes to fit local tool architectures.
* **Active In-Process Merger:** Pipelines successful out-of-tree workspace binaries straight back into the live core application tree via thread-safe runtime hot-swapping.

---

## ⚙️ Configuration Setup (`blueprint.aero`)

The execution of the optimization pipeline is governed by a `blueprint.aero` manifest file placed at the root of your workspace. This file defines your target compilation sources, analytical boundaries, and compiler toolchains using strict TOML formatting.

### 🧱 Manifest Structural Breakdown

* **`[system]`**: Sets global pipeline strategies and defines whether optimized variants are treated as volatile execution paths.
* **`[context_registry.<target_name>]`**: Explicitly registers target files for analysis, declaring their native language patterns and preservation settings.
* **`[scaling]`**: Establishes the static analysis boundaries. Files exceeding these metrics automatically trigger structural fragmentation and module decomposition sweeps.
* **`[graph]`**: Configures the compilation pipeline array. Inline tables defined here **must use standard TOML syntax (`=`)** instead of JSON colons (`:`) to ensure proper loading.
* **`[compiler]`**: Sets target toolchain profiles and defines optimization aggression constraints.

### Production Blueprint Example

```toml
[system]
name = "production-scale-polyglot-pipeline"
strategy = "universal-engine"
ephemeral_code = true

# 1. Register Build Targets
[context_registry.core_application]
path = "./src/app_logic.py"
language = "python"
preserve_original_logic = false

[context_registry.native_backend]
path = "./src/lib.rs"
language = "rust"
preserve_original_logic = false

# 2. Define Analytical Scaling Constraints
[scaling]
auto_split_threshold = 120       # Line limits per function scope triggering auto-decomposition
max_module_complexity = 12       # Maximum McCabe cyclomatic complexity allowed before intervention
hierarchy_depth = 4              # Maximum allowed package nesting depth

# 3. Configure Output Graph (Note: Inline tables must use '=' assignment)
[graph]
targets = [
    { name = "core_application", source = "translator/core_orchestrator.py", output = "build_artifacts/core_orchestrator.optimized.py" },
    { name = "native_backend", source = "translator/anyon_extension.py", output = "build_artifacts/anyon_extension.optimized.py" }
]
dependencies = []
boundaries = ["core_application"]

# 4. Bind Compiler Parameters
[compiler]
toolchain = "python3"
optimization_level = "aggressive"

```

---

## 🛠️ CLI Reference Manual

AeroNova exposes a comprehensive systems command-line interface to orchestrate static builds, dependency graph visualizations, and automated repair cycles. All core pipeline invocations require an explicit subcommand verb flag.

### Run Pipeline Build

Executes the full optimization loop, analyzing dependency graphs, evaluating caches, running multi-objective parameter sweeps, and executing code-generation cycles:

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

```

```
