# Aero Nova

Aero Nova is a deterministic, self-evolving, multi-agent build optimization and pipeline orchestration engine. Rather than executing static compile-and-link steps, Aero Nova models the build and compilation lifecycle as a **multi-objective optimization problem**. It employs static analysis, AST-level compaction, and an evolutionary tuner to discover Pareto-optimal configurations that balance execution speed, code size, and target accuracy.

While the **Aero Build Engine** serves as a static, non-evolving runtime extraction, **Aero Nova** represents the full, active super-system—integrating a multi-agent feedback loop (**the Cortex**) that dynamically mutates and evolves build parameters over successive runs.

---

## Key Architectural Pillars

### 1. The Cortex (Multi-Agent Decider Loop)

Unlike static build systems, Aero Nova uses a coordinated multi-agent runtime layer to monitor and direct optimizations:

* **Accuracy Guard:** Monitors code coverage metrics, test outputs, and compiler safety floors. It halts or rolls back mutations that drop below the user-defined `target_accuracy_floor`.
* **Performance Profiler:** Measures micro-benchmarks and total wall-time across build cycles to quantify execution latencies.
* **Compactor Agent:** Assesses code density and AST complexity, tuning AST compaction and minification depth.

### 2. Multi-Objective Optimization (NSGA-II)

Aero Nova tracks and optimizes three conflicting physical objectives:

1. **Accuracy (Reliability):** Code coverage validation and test suite assertions.
2. **Speed (Execution Latency):** Minimizing compile-time and run-time execution paths.
3. **Compression (Structural Density):** AST-level file size and overhead reduction.

The system runs a Non-Dominated Sorting Genetic Algorithm (**NSGA-II**) across multiple generations to maintain a **Pareto Frontier** of build configurations, allowing developers to choose the optimal trade-off point for their specific production target.

```text
        ▲ [Speed] (Low execution time)
        │
        │      ● (Candidate A: Hyper-fast, minimal compaction)
        │     ╱
        │   ● (Candidate B: Balanced Pareto-optimal)
        │  ╱
        │● (Candidate C: Maximally compacted, slower build)
        └────────────────────────────────────────► [Compression] (Reduced size)

```

### 3. AST-Level Compaction (Tree-sitter Engine)

Aero Nova integrates native tree-sitter parsers to safely parse and reconstruct syntax trees:

* **Dead-Code Elimination (DCE):** Multi-pass recursive analysis to prune unreferenced variables, uncalled functions, and unreachable execution branches.
* **Unused Import Removal:** Resolves and strips dangling namespace imports.
* **Scope-Aware Minification:** Executes alpha-renaming on local variable bindings with collision-safe salting to ensure original runtime behavior remains unchanged.

### 4. Graph-Based Incremental Orchestration

The execution layer models tasks as a Directed Acyclic Graph (**DAG**):

* **Deterministic Scheduling:** Dependency trees are checked via a three-state Depth-First Search (DFS) coloring algorithm to intercept and report cyclic dependencies.
* **Cryptographic Fingerprinting:** Monitored targets are hashed with SHA-256. If neither the source files nor their upstream dependency subtrees have mutated, the execution step short-circuits to cache.

---

## Pipeline Lifecycle

```text
   blueprint.aero
        │
        ▼
   ┌───────────┐       ┌────────────────┐       ┌─────────────────┐       ┌───────────┐
   │  Scanner  │ ───►  │ Decision Tree  │ ───►  │ Parameter Tuner │ ───►  │ Compactor │
   └───────────┘       └────────────────┘       └─────────────────┘       └───────────┘
        ▲                                                │                      │
        │                                                ▼                      │
        │                                            [NSGA-II]                  ▼
        └──────────────────────────────────────  Cortex Feedback ◄─────  Translator (.aeroc)

```

1. **Scan:** Static parser evaluates directories, resolving file boundaries and calculating initial AST hashes.
2. **Evaluate & Schedule:** Resolves the dependency DAG and schedules non-interdependent tasks across a dynamic worker thread pool.
3. **Evolve & Tune:** The Cortex agent population evaluates target metrics against historical runs, generating parameter mutations.
4. **Compact:** Tree-sitter transforms syntax trees based on the elected optimization profile.
5. **Translate:** Emits optimized targets and serializes compilation actions into Aero recipe files (`.aeroc`).

---

## Configuration (`blueprint.aero`)

Build targets and Cortex objectives are defined in a declarative manifest file, typically placed at the root of the workspace:

```json
{
  "project": {
    "name": "aero-nova-app",
    "version": "1.0.0"
  },
  "cortex": {
    "target_accuracy_floor": 0.9950,
    "evolution_generations": 100,
    "population_size": 25,
    "mutation_rate": 0.15,
    "agents": ["accuracy_guard", "performance_profiler", "ast_compactor"]
  },
  "targets": {
    "shared_lib": {
      "path": "src/core",
      "language": "python",
      "dependencies": [],
      "compiler_flags": ["-O3"],
      "opt_level": 2
    },
    "entrypoint": {
      "path": "src/app",
      "language": "python",
      "dependencies": ["shared_lib"],
      "compiler_flags": [],
      "opt_level": 3
    }
  }
}

```

---

## Getting Started

### Prerequisites

* **Python:** Version 3.10 or higher.
* **C++ Compiler:** *(Optional, required only if compiling tree-sitter language parsers from source)*.

### Installation

Clone the repository and install runtime dependencies:

```bash
git clone https://github.com/sys1own/aero-nova.git
cd aero-nova
pip install -r requirements.txt

```

---

## CLI Reference

Aero Nova exposes a clean command-line interface to orchestrate static compilations and evolutionary optimization loops:

### Run Build

Executes the build pipeline based on the current Pareto-frontier or default configurations:

```bash
python main.py run --blueprint blueprint.aero

```

### Optimize Hyperparameters

Launches a multi-agent evolutionary tuning sequence to find more optimal compiler parameters:

```bash
python main.py tune --generations 50 --pop-size 20

```

### Inspect Pipeline Status

Visualizes the resolved dependency graph, cache hits, and performance history:

```bash
python main.py status

```

### Evict Cache

Cleans execution caches and temporary build artifacts:

```bash
python main.py clean

```

---

## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
