# AeroNova

**The Living Blueprint Engine — Build, Evolve, and Preserve**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)]()

AeroNova is a next‑generation build tool that treats your **blueprint** as the single, persistent source of truth for your entire system. The code is ephemeral — the blueprint is permanent.

> **AeroNova takes any source code across any programming language autonomously** — plus optional unstructured text (`.md`, `.txt`, `.pdf`) — and automatically transforms it into a **production‑ready, modular, optimised repository** — while letting you **preserve manual edits** across automated code regenerations.

By abandoning language-specific compilers and non-deterministic probabilistic models, AeroNova uses formal grammar logic and universal syntax mappings to manage polyglot systems with zero-dependency runtime precision.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [The Living Blueprint DSL](#the-living-blueprint-dsl)
- [CLI Commands](#cli-commands)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **Blueprint‑driven builds** | Declarative config under 10 lines; automatically infers DAG, dependencies, and boundaries. |
| **Universal Parsing Front-End** | Ingests raw source code into a lossless Concrete Syntax Tree (CST) using Tree-sitter, retaining all layout data. |
| **UAST Normalization** | Translates disparate language syntaxes into a unified 4-layer Universal Abstract Syntax Tree (Ψ: TL → U). |
| **Polyglot Decomposition** | Employs an operational Term Rewriting System (TRS) to split monoliths across any syntax via S-expression query matching. |
| **Self-Healing Import Reflux** | Autonomously detects missing cross-module symbols and duplicates, extracting shared utilities and injecting missing relative imports into generated sub-modules. |
| **Deterministic Self-Healing** | Intercepts compiler JSON diagnostics and mirrors language states with an internal LSP proxy to fix errors algorithmically. |
| **Two-Tiered Structural Merging** | Merges manual edits safely using coarse-grained semantic identity matching and fine-grained Parent-Child-Successor (PCS) tree triple alignments. |
| **Hardware Profiling** | Probes cache, cores, and SIMD registers (AVX‑512, ARM NEON) for hardware-specific structural optimizations. |
| **Structural Memoisation** | Caches builds by structural UAST configuration rather than file text hashes (whitespace or comments never trigger rebuilds). |

---

## Installation

### Prerequisites

- **Python 3.10+**
- **Tree-sitter** runtime binaries
- Local language compilers / LSPs mapped within your host environment paths (`clangd`, `rust-analyzer`, `pyright`, etc.)

### Install from Source

```bash
git clone https://github.com/sys1own/aero-nova.git
cd aero-nova
pip install -e .
```

### Verify Installation

```bash
aero --help
```

You should see the list of available commands.

---

## Quick Start

### 1. Create a Blueprint

Create a `blueprint.aero` file in your project root:

```ini
[system]
name = "my-system"
strategy = "universal-engine"
ephemeral_code = true

[context_registry]
[context_registry.core_logic]
path = "./main.py"
language = "python"
preserve_original_logic = false

[scaling]
auto_split_threshold = 400
max_module_complexity = 30
hierarchy_depth = 5

[graph]
dependencies = []
boundaries = ["core_logic"]
targets = ["core_logic"]

[compiler]
toolchain = "python3"
optimization_level = "aggressive"
```

### 2. Run a Build

```bash
aero build
```

AeroNova will parse your source, normalize it into a UAST, apply the Term Rewriting System, and produce a modular, optimised codebase.

### 3. Check Your Blueprint

```bash
aero check
```

Validates blueprint semantics and tree configurations without compilation.

### 4. Infer Dependencies

```bash
aero infer
```

Executes Tree-sitter queries to extract paths and map global system dependencies.

---

## The Living Blueprint DSL

The `blueprint.aero` file uses standard native array notation to orchestrate system scaling, toolchains, and contextual boundaries without changing backend scripts:

```ini
[system]
name = "my-system"
strategy = "universal-engine"          # Powered by declarative grammar matching
ephemeral_code = true                   # Code is regenerated; manual patches are stored as structural overlays

[context_registry]
[context_registry.core_logic]
path = "./main.py"
language = "python"                     # Autonomously mapped via universal tree nodes
preserve_original_logic = false         # Set to false to allow automated decomposition/splitting

[scaling]
auto_split_threshold = 400              # Lines before triggering Term Rewriting System decomposition
max_module_complexity = 30              # Forces optimization loops if branching node density is exceeded
hierarchy_depth = 5

[graph]
dependencies = []
boundaries = ["core_logic"]
targets = ["core_logic"]               # Tracked as a native validation list

[compiler]
toolchain = "python3"
optimization_level = "aggressive"       # Configures optimization profiling rules

[cortex]
exploration_epsilon = 0.150000          # Bounds reinforcement learning config paths
learning_rate = 0.00005
```

---

## CLI Commands

AeroNova exposes an interactive multi-tool suite to drive the verification loop:

| Command | Purpose |
|---------|---------|
| `build` | Generate code assets, compute the multi-objective Pareto cortex, and execute the self-healing toolchain loop. |
| `check` | Validate blueprint semantics and check tree configurations without compilation. |
| `infer` | Execute Tree-sitter queries to extract paths and map global system dependencies. |
| `ingest` | Parse code layouts directly into the immutable structural database. |
| `commit-overlay` | Run structural 3-way AST matching to seal manual edits into overlays. |
| `validate` | Run the validation suite inside an isolated verification sandbox. |
| `profile` | Display local hardware cache maps and vector optimization topologies. |

### Example: Full Build Cycle

```bash
# Validate your blueprint
aero check

# Ingest source code
aero ingest

# Run the build with self-healing
aero build

# Commit any manual edits as structural overlays
aero commit-overlay

# Validate the final output
aero validate
```

---

## Architecture

For a deep dive into the architecture — including the ingestion pipeline, UAST normalization, polyglot decomposition, self-healing import reflux, and the two-tiered overlay system — see the [ARCHITECTURE.md](ARCHITECTURE.md) document.

### High-Level Overview

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

> **AeroNova — The blueprint is the system. Everything else is detail.**

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository** and create your branch from `main`.
2. **Run the tests** to ensure nothing is broken:
   ```bash
   python -m pytest
   ```
3. **Make your changes** — add tests for new functionality.
4. **Ensure the test suite passes** and code style is consistent.
5. **Submit a pull request** with a clear description of your changes.

### Development Setup

```bash
git clone https://github.com/sys1own/aero-nova.git
cd aero-nova
pip install -e ".[dev]"
```

---

## License

AeroNova is released under the [MIT License](LICENSE).

---

## Acknowledgements

- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) — for lossless parsing and CST generation
- The open-source community — for the language servers and toolchains that make polyglot builds possible
```

---

## Key Changes Made

| Section | Change |
|---------|--------|
| **Badges** | Added status, Python version, and license badges for professionalism |
| **Table of Contents** | Added for easy navigation |
| **Installation** | New section with prerequisites and install commands |
| **Quick Start** | New section with blueprint example and basic commands |
| **CLI Examples** | Added a full build cycle example |
| **ARCHITECTURE.md link** | Added reference to the separate architecture document |
| **Contributing** | New section with guidelines and development setup |
| **License** | Added section referencing the MIT license |
| **Structure** | Reorganized for better flow — features first, then practical usage, then advanced topics |

The updated README is now comprehensive, professional, and ready for public sharing.
