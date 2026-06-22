# AeroNova

**The Living Blueprint Engine — Build, Evolve, and Preserve**

AeroNova is a next‑generation build tool that treats your **blueprint** as the single, persistent source of truth for your entire system. The code is ephemeral — the blueprint is permanent.

---

## What AeroNova Does (Today)

AeroNova takes any source code (single‑file or multi‑file, across Python/Rust/C++), plus optional unstructured text (`.md`, `.txt`, `.pdf`), and automatically transforms it into a **production‑ready, modular, optimised repository** — while letting you **preserve manual edits** across regenerations.

### Core Capabilities (All Implemented)

| Feature | Description |
|---------|-------------|
| **Blueprint‑driven builds** | Declarative config (`blueprint.aero`) under 10 lines; infers DAG, dependencies, FFI boundaries. |
| **Multi‑language compilation** | Rust (`cargo`), Python, C++ via a pluggable microkernel. |
| **Modular decomposition** | Splits monolithic Python scripts into multi‑file packages via AST analysis. |
| **Static import pruning** | Removes unused imports per generated module. |
| **Cross‑module interlinking** | Injects relative imports between sibling modules. |
| **Multi‑file source merging** | Merges ASTs from multiple input files before decomposition. |
| **Self‑test scaffolding** | Generates `tests/` directory with import‑validation tests. |
| **Rust auto‑correction** | On build failure (e.g., `let x` → `let mut x`), re‑dispatches build once. |
| **Hardware profiling** | Probes cache, cores, SIMD (AVX‑512, ARM NEON). |
| **AST‑level memoisation** | Caches by AST structure, not file hashes (whitespace/comments don't trigger rebuilds). |
| **Semantic fluidity (text ingestion)** | Parses `.md`, `.txt`, `.pdf` for relational logic, definitions, mathematical assignments. |

### Living Blueprint DSL (New)

The `blueprint.aero` file now supports a richer schema designed for **continuous evolution**:

```toml
[system]
name = "my-system"
strategy = "microkernel"          # microkernel | layered | hexagonal | monolith-reducer
ephemeral_code = true             # Code is regenerated; manual patches are stored as overlays

[context_registry]
  # Ingested contexts (added via `ingest` command)
  [context_registry.payroll]
  path = "./legacy/payroll.cob"   # example; future language support
  language = "cobol"              # currently parsed for future plugins
  preserve_original_logic = true

[abstractions]
  # Placeholder for future rewrite rules (e.g., legacy → modern patterns)
  # [[abstractions.rewrite]]
  # legacy_pattern = "PERFORM VARYING ... UNTIL"
  # target_pattern = "Rust Iterators + fold"

[scaling]
  auto_split_threshold = 1500     # Lines before auto-decomposition
  max_module_complexity = 200     # Cyclomatic complexity per module
  hierarchy_depth = 4

[context_bridges]
  # Placeholder for future cross‑context integration (FFI, gRPC, sidecars)
  # [[context_bridges]]
  # source = "ai_lib"
  # target = "payroll"
  # bridge_type = "grpc_sidecar"
```

**The parser understands all these sections** – they are designed to be extended as we add more advanced capabilities.

### Context Registry & Semantic Hashing

- The `ingest` command stores every ingested codebase in an **immutable AST database**.
- Each function and module is assigned a **semantic hash** based on its AST (ignoring whitespace/comments).
- Duplicate or similar code across contexts is automatically detected and unified.

### Overlay System (Manual Edit Preservation)

- After a `build`, you can manually edit any generated file.
- Run `aero commit-overlay <file>` – the diff is captured as a **patch overlay**.
- On subsequent `build`s, your overlays are **surgically reapplied** to the freshly generated code.
- Your custom logic survives regenerations – the blueprint remains the sole architectural source.

---

## CLI Commands (All Active)

| Command | Purpose |
|---------|---------|
| `build` | Generate and compile the system from the blueprint. |
| `check` | Validate the blueprint and contexts without building. |
| `infer` | Infer DAG and dependencies from existing sources. |
| `ingest` | Ingest source files into the context registry (with semantic hashing). |
| `scaffold` | Generate skeleton code for new modules. |
| `profile` | Display hardware profile (cache, cores, SIMD). |
| `cache` | Manage AST memoisation cache. |
| `libraries` | List available library dependencies. |
| `validate` | Run the generated test suite. |
| `runtime` | Execute the built system. |
| `invariants` | Check system‑wide invariants (e.g., type consistency). |
| `polymorphize` | Apply hardware‑specific optimisations (SIMD, alignment). |
| `plan` | Show the build plan (DAG) without executing. |
| `analyze` | Analyse code complexity and dependencies. |
| `shield` | Generate a dependency shield (e.g., for license compliance). |

---

## Quick Start

```bash
# Clone and enter
git clone https://github.com/sys1own/aero-nova.git
cd aero-nova

# Install Python dependencies
pip install -r requirements.txt

# Ingest a codebase (e.g., a Python project)
python main.py ingest --path ./my_project --context-name my_project --language python

# Build the system
python main.py build

# Manual edit a generated file, then preserve it
python main.py commit-overlay ./build/src/my_module.py

# Rebuild – your edit remains
python main.py build
```

---

## System Requirements

- **Python 3.8+**
- **Rustup / Cargo** (latest stable)
- **System C libraries** for arbitrary‑precision math:
  - Ubuntu/Debian: `sudo apt install libgmp-dev libmpfr-dev libmpc-dev`
  - macOS: `brew install gmp mpfr libmpc`

---

## What’s Planned (Future)

- **Legacy language modernisation** (COBOL, PL/I, Fortran) with user‑definable rewrite rules.
- **Multi‑context FFI generation** (automatic bridges between Rust, Python, Java, etc.).
- **Blueprint Federation** – split the blueprint into sub‑blueprints for enterprise scale.
- **Autonomous repair loop** – LLM‑assisted compilation error fixing.

These features are designed into the architecture (see `[abstractions]` and `[context_bridges]`), but are not yet implemented.

---

## Architecture Overview

```
blueprint.aero (Living DSL)
        │
        ▼
DAG Inference Engine (Context Registry + Federation)
        │
        ├── Hardware Profiler (Real‑time topology)
        ├── Semantic Fluidity (Unstructured context ingestion)
        └── AST Cache & Overlay System
        │
        ▼
Polymorphic Rewriter (Memory mapping & SIMD patching)
        │
        ▼
Pluggable Microkernel Compilation (C++ / Rust / Python / …)
        │
        ▼
Incremental Build Output (with Overlay Re‑application)
```

---

## Contributing

AeroNova is an open‑source research project. We welcome contributions, bug reports, and feature ideas. Please open an issue or pull request.

---

## License

[Specify your license]

---

**AeroNova — The blueprint is the system. Everything else is detail.**
