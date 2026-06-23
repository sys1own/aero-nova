"""
reflux.py — Aero Dependency Reflux Engine

Applies the structured mutation commands produced by
:class:`src.lsp_proxy.LspDiagnosticRefluxBinder` to source files in memory,
healing higher-level semantic defects (undefined symbols, missing imports,
unresolved Rust modules) before the compiler executes.

All patches operate on an in-memory copy of the file content; the returned
``bytes`` carry the mutated source so callers can either persist it or hand it
straight to the compilation pipeline without touching disk.

Supported actions:
  - ``RESOLVE_UNDEFINED_SYMBOL``    (Python) -> ``from aero_nova.core import {symbol}``
  - ``AUTO_REFLUX_IMPORT``          (Python) -> ``import {target}``
  - ``INJECT_RUST_USE_DECLARATION`` (Rust)   -> ``use crate::modules::{item};``
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AeroDependencyRefluxEngine:
    """Apply LSP-derived reflux patches to a source file's bytes."""

    AERO_CORE_NAMESPACE = "aero_nova.core"
    RUST_MODULE_NAMESPACE = "crate::modules"

    def apply_reflux_patches(
        self, file_path: str, actions: List[Dict[str, Any]]
    ) -> bytes:
        """Apply every reflux action to ``file_path`` and return mutated bytes.

        The file is read once, mutated in memory line-by-line, and returned as
        UTF-8 encoded bytes. Unknown actions and actions lacking a usable symbol
        are skipped (logged), leaving the source untouched for that entry.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning("reflux: cannot read %s: %s", file_path, exc)
            return b""

        lines = text.splitlines(keepends=True)

        for action in actions:
            kind = action.get("action")
            symbol = action.get("symbol") or action.get("target")

            if not symbol:
                logger.debug("reflux: skipping action without symbol: %r", action)
                continue

            if kind == "RESOLVE_UNDEFINED_SYMBOL":
                lines = self._inject_python_core_import(lines, symbol)
            elif kind == "AUTO_REFLUX_IMPORT":
                lines = self._inject_python_import(lines, symbol)
            elif kind == "INJECT_RUST_USE_DECLARATION":
                lines = self._inject_rust_use(lines, symbol)
            else:
                logger.debug("reflux: unknown action kind %r", kind)

        return "".join(lines).encode("utf-8")

    # ------------------------------------------------------------------ #
    # Python patches
    # ------------------------------------------------------------------ #
    def _inject_python_core_import(
        self, lines: List[str], symbol: str
    ) -> List[str]:
        """Inject ``from aero_nova.core import {symbol}`` after the docstring/comments."""
        statement = f"from {self.AERO_CORE_NAMESPACE} import {symbol}\n"
        if self._statement_present(lines, statement):
            return lines
        insert_at = self._python_header_offset(lines)
        return lines[:insert_at] + [statement] + lines[insert_at:]

    def _inject_python_import(self, lines: List[str], target: str) -> List[str]:
        """Insert ``import {target}`` at the head of the file (after the header)."""
        statement = f"import {target}\n"
        if self._statement_present(lines, statement):
            return lines
        insert_at = self._python_header_offset(lines)
        return lines[:insert_at] + [statement] + lines[insert_at:]

    @staticmethod
    def _python_header_offset(lines: List[str]) -> int:
        """Return the line index immediately following module docstrings/comments.

        Skips a leading shebang, encoding/comment lines, blank lines, and a
        module-level triple-quoted docstring so injected imports land in a
        syntactically valid position.
        """
        idx = 0
        n = len(lines)

        # Leading comments, shebangs and blank lines.
        while idx < n:
            stripped = lines[idx].strip()
            if stripped == "" or stripped.startswith("#"):
                idx += 1
            else:
                break

        # Module-level docstring.
        if idx < n:
            stripped = lines[idx].lstrip()
            for quote in ('"""', "'''"):
                if stripped.startswith(quote):
                    # Single-line docstring.
                    rest = stripped[len(quote):]
                    if rest.rstrip().endswith(quote) and len(stripped.rstrip()) > len(quote):
                        idx += 1
                    else:
                        idx += 1
                        while idx < n and quote not in lines[idx]:
                            idx += 1
                        if idx < n:
                            idx += 1  # consume the closing-quote line
                    break

        return idx

    @staticmethod
    def _statement_present(lines: List[str], statement: str) -> bool:
        """True when ``statement`` already exists (idempotency guard)."""
        target = statement.strip()
        return any(line.strip() == target for line in lines)

    # ------------------------------------------------------------------ #
    # Rust patches
    # ------------------------------------------------------------------ #
    def _inject_rust_use(self, lines: List[str], item: str) -> List[str]:
        """Prepend ``use crate::modules::{item};`` to the file."""
        statement = f"use {self.RUST_MODULE_NAMESPACE}::{item};\n"
        if self._statement_present(lines, statement):
            return lines
        insert_at = self._rust_header_offset(lines)
        return lines[:insert_at] + [statement] + lines[insert_at:]

    @staticmethod
    def _rust_header_offset(lines: List[str]) -> int:
        """Return the index after leading Rust comments / attributes / blanks."""
        idx = 0
        n = len(lines)
        while idx < n:
            stripped = lines[idx].strip()
            if (
                stripped == ""
                or stripped.startswith("//")
                or stripped.startswith("#![")  # inner attributes / crate attrs
            ):
                idx += 1
            else:
                break
        return idx
