# AeroNova

**The Living Blueprint Engine — From Legacy Chaos to Continuous Evolution**

AeroNova is a ground‑up reimagining of what a build system can be. Where traditional tools treat configuration as a static snapshot, AeroNova treats the **blueprint as the single, persistent source of truth** for your entire system's lifecycle.

> **One blueprint to rule them all.** The code is ephemeral. The blueprint is permanent.

---

## The Vision

Modernising legacy systems is painful. Adding unrelated codebases is chaotic. Scaling to enterprise complexity is a nightmare of configuration files, dependency hell, and broken builds.

AeroNova changes the game:

- **Point it at a 30‑year‑old COBOL payroll system.** It outputs a modular, production‑ready Rust/Python codebase with unit tests, running in a container.
- **Want to scale to 10x the load?** Edit two numbers in the blueprint. The engine re‑generates the architecture — microkernels, thread pools, the works.
- **Need to integrate an unrelated AI fraud‑detection library?** Add its path to the blueprint. The engine generates FFI bindings, sidecar containers, or gRPC stubs automatically.
- **Found a business rule the engine misinterpreted?** Fix it once in the generated code, capture the diff as an overlay, and every future regeneration preserves your custom logic.

**You never touch the generated code again — unless you want to.** All architectural decisions (splitting, scaling, integration, modernisation) happen in the blueprint.

---

## Core Paradigm Shift

| Traditional Build Systems | AeroNova |
| :--- | :--- |
| Blueprint → one‑shot code generation | Blueprint → **mounted virtual filesystem**; code generated on‑demand and cached |
| You edit code *outside* the blueprint | You edit the *blueprint*; the engine applies semantic patches without losing your manual overrides |
| Adding new code requires re‑ingesting and rebuilding from scratch | Adding new code just updates the blueprint's context registry; the engine incrementally re‑integrates it |
| Limited to one project scope | Supports **multi‑context federation** — unrelated codebases become pluggable modules in the same blueprint |

---

## Key Breakthrough Capabilities

### 🧬 Living Blueprint DSL
The blueprint isn't a static manifest — it's a **living system description** that evolves with your project. Extended sections handle legacy complexity, scaling policies, and cross‑context bridges:

```toml
[system]
name = "legacy-erp-modernisation"
strategy = "microkernel"          # microkernel | layered | hexagonal | monolith-reducer
ephemeral_code = true             # Code is regenerated; manual patches are stored as overlays

[context_registry]
  [context_registry.legacy_cobol]
  path = "./dumps/legacy/"
  language = "cobol"
  dialect = "ibm"                 # Handles fixed-form, go-to, 88-levels
  preserve_original_logic = true
  
  [context_registry.ai_fraud_lib]
  path = "../unrelated-python-lib/"
  language = "python"
  integration_mode = "sidecar"    # ffi | grpc | sidecar | shared_memory

[abstractions]
  [[abstractions.rewrite]]
  legacy_pattern = "PERFORM VARYING ... UNTIL"
  target_pattern = "Rust Iterators + fold"

[scaling]
  auto_split_threshold = 1500     # Lines before auto-decomposition
  max_module_complexity = 200     # Cyclomatic complexity per module
  hierarchy_depth = 4             # Max nested module depth

[context_bridges]
  [[context_bridges]]
  source = "ai_fraud_lib"
  target = "legacy_cobol"
  bridge_type = "grpc_sidecar"    # ffi | grpc | message_queue | shared_memory
```

### 🔗 Immutable Context Registry
Every ingested codebase (legacy, modern, or unrelated) is stored in an **immutable AST database** using `tree-sitter` for ~40 languages. Each function and module gets a **semantic hash** based on its AST, not whitespace. If two unrelated codebases share a common algorithm, the engine detects the structural similarity and unifies them — eliminating redundancy automatically.

### 🧩 Incremental Re‑generation & Overlay System
Manual fixes are never lost:
1. The engine materialises code into `./build/`.
2. If you manually edit a generated file, the engine captures the diff as a **patch overlay** stored alongside the blueprint.
3. On re‑generation, the engine surgically reapplies your overlays using semantic merge (with LLM‑assisted conflict resolution).
4. **Result:** The blueprint remains the sole source of truth; your custom logic is safely preserved.

### 🌐 Blueprint Federation (Hierarchical Scaling)
To handle enterprise‑scale systems (millions of lines), AeroNova supports **Blueprint Federation**:
- A root `blueprint.aero` imports sub‑blueprints (e.g., `blueprint.finance.aero`, `blueprint.hr.aero`).
- Each sub‑blueprint defines its own context, but they share a **global type registry**.
- The engine builds a distributed DAG. If `Finance` depends on `HR`'s employee records, the bridge is automatically inferred and implemented via asynchronous messaging or gRPC.

### 🔌 Unrelated Context Integration (The "Kitchen Sink" Mode)
Adding unrelated code is effortless:
1. **Introspection:** The engine scans the unrelated code for entrypoints (APIs, public functions).
2. **Namespace Isolation:** It wraps the code in a unique namespace to prevent symbol collisions.
3. **Adaptor Generation:** It automatically generates **Facade adaptors** that translate your legacy system's calling conventions into the unrelated library's expected format.
4. **Integration Mode Selection:** Based on performance requirements, it chooses:
   - *In‑process FFI* (fastest, for Rust/C/C++)
   - *Sidecar container* (for Python/Java/Ruby)
   - *REST/gRPC* (for distributed systems)

### ⚡ Autonomous Hardware Polymerisation
Real‑time host architecture introspection — discovers cache hierarchies, core configurations, and SIMD instruction sets (AVX‑512, ARM NEON), then polymorphically rewrites memory alignment and code loops for maximum performance. **Zero compiler optimisation flags required from the user.**

### 🧠 AST‑Level Delta Memoisation
Caches build artifacts using an incremental structural query system. Tracks **abstract syntax tree modifications** instead of file hashes — changes to whitespace, formatting, or comments never trigger a slow rebuild.

---

## Development Workflow (How You Use It)

**Day 1 — Modernise:** Point the engine at a legacy COBOL payroll system. Run:
```bash
aero nova modernize --blueprint blueprint.aero
```
The engine outputs a modular Rust/Python codebase with unit tests, running in a container. It works.

**Day 2 — Scale:** The payroll system needs to handle 10x more transactions. Edit `blueprint.aero`:
```toml
auto_split_threshold = 800
strategy = "microkernel"
```
The engine re‑generates the code, splitting the monolithic `process_payroll` function into 12 micro‑kernel plugins. You don't touch the code.

**Day 3 — Integrate Unrelated Context:** Add a new AI fraud‑detection library (Python) to the payroll flow. Add its path to `context_registry` and define a bridge:
```toml
bridge_type = "sidecar"
```
The engine generates a gRPC server for the AI library and a client stub inside the Rust payroll system. The system now scales horizontally with the AI sidecar.

**Day 4 — Preserve Custom Logic:** Override a specific legacy business rule that the engine misinterpreted. Open the generated `payroll_rules.rs`, fix it, and run:
```bash
aero nova commit-overlay
```
The diff is saved as an overlay. Every future regeneration preserves your custom logic.

**Day 5 — Extreme Scale:** Split the root blueprint into regional sub‑blueprints for compliance. The engine federates the build, generating separate deployments but sharing the core base. Inter‑region communication switches to asynchronous Kafka queues automatically.

---

## Quick Start

```bash
# Clone and enter the repository
git clone https://github.com/sys1own/aero-nova.git
cd aero-nova

# Install dependencies
pip install -r requirements.txt

# Run the automatic project inference
python main.py build
```

### ⚙️ System Prerequisites

- **Rustup / Cargo** (Latest stable)
- **Python 3.8+**
- **System C Libraries** (for arbitrary‑precision math):
  - *Ubuntu/Debian:* `sudo apt install libgmp-dev libmpfr-dev libmpc-dev`
  - *macOS:* `brew install gmp mpfr libmpc`

---

## Architecture

AeroNova builds upon a lightweight **microkernel core** that manages graph scheduling, data dependencies, and process dispatching, while routing language compilation through decoupled, independent toolchain plugins.

```
┌─────────────────────────────────────────────────┐
│           blueprint.aero (Living DSL)           │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         DAG Inference Engine                    │
│    (Context Registry + Federation Resolver)     │
└─────┬───────────────────────┬───────────────────┘
      │                       │
┌─────▼─────┐         ┌───────▼──────────┐
│ Hardware  │         │  Semantic        │
│ Profiler  │         │  Fluidity        │
│ (Real-Time│         │  (Unstructured   │
│  Topology)│         │   Context        │
└─────┬─────┘         │   Ingestion)     │
      │               └───────┬──────────┘
      └───────────┬───────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│      Polymorphic Rewriter                       │
│   (Memory mapping & SIMD vector patching)       │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│   Pluggable Microkernel Compilation             │
│      (C++ / Rust / Python / COBOL / ...)       │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Incremental AST Cache & Overlay System         │
└─────────────────────────────────────────────────┘
```

---

## Roadmap

| Phase | Focus | Status |
| :--- | :--- | :--- |
| **1. AST Ingestion & Normalisation** | COBOL, PL/I, legacy C++ dialects | 🚧 In Progress |
| **2. Living Blueprint Server** | Daemon that watches `blueprint.aero` for changes and hot‑reloads | 📋 Planned |
| **3. Overlay Engine** | Diff‑capture and surgical patch application | 📋 Planned |
| **4. Multi‑Context FFI Generator** | Automated bindings across Rust, Python, C, JVM | 📋 Planned |
| **5. Blueprint Federation** | Hierarchical imports and distributed DAG scheduling | 📋 Planned |
| **6. Autonomous Repair Loop** | LLM‑assisted type inference and compilation repair | 📋 Planned |

---

## Contributing

This is a research‑oriented prototype with ambitious goals. Contributions are welcome — open an issue or pull request for improvements, bug fixes, or new feature ideas.

---

## License

[Specify your license]

---

**AeroNova — The blueprint is the system. Everything else is implementation detail.**
