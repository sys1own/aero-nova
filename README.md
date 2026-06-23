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
- [Self-Hosting & Bootstrapping](#self-hosting--bootstrapping)
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
| **Staging Self-Hosting Core** | Supports self-targeting builds via an isolated shadow staging area and automated validation check pass before performing an atomic swap on disk. |
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
git clone [https://github.com/sys1own/aero-nova.git](https://github.com/sys1own/aero-nova.git)
cd aero-nova
pip install -e .
