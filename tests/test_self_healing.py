# -*- coding: utf-8 -*-
"""Tests for the deterministic self-healing compilation wrapper."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from core.toolchain.self_healing import (
    Category,
    Diagnostic,
    SymbolIndex,
    _apply_edits,
    _plan_edits,
    categorize,
    flag_healing_failure,
    heal_module,
    make_rust_build_fn,
    parse_rustc_json,
)


def _has(b):
    return shutil.which(b) is not None


_RUSTC_JSON = (
    '{"$message_type":"diagnostic","message":"cannot assign twice to immutable variable `x`",'
    '"code":{"code":"E0384"},"level":"error","spans":[{"file_name":"a.rs","byte_start":21,'
    '"byte_end":22,"line_start":1,"column_start":1,"is_primary":true}]}\n'
    '{"$message_type":"diagnostic","message":"aborting due to 1 previous error","level":"error","spans":[]}\n'
)


class TestDiagnosticParsing(unittest.TestCase):
    def test_parse_rustc_json(self):
        diags = parse_rustc_json(_RUSTC_JSON)
        self.assertEqual(len(diags), 1)
        d = diags[0]
        self.assertEqual(d.code, "E0384")
        self.assertEqual(d.start_byte, 21)
        self.assertEqual(d.source, "rustc")


class TestCategorize(unittest.TestCase):
    def test_codes(self):
        self.assertEqual(categorize(Diagnostic("x", "f", code="E0432")), Category.MISSING_IMPORT)
        self.assertEqual(categorize(Diagnostic("x", "f", code="E0384")), Category.IMMUTABLE_ASSIGNMENT)

    def test_messages(self):
        self.assertEqual(
            categorize(Diagnostic('"foo" is not defined', "f")), Category.MISSING_IMPORT)
        self.assertEqual(
            categorize(Diagnostic("cannot assign twice to immutable variable `x`", "f")),
            Category.IMMUTABLE_ASSIGNMENT)
        self.assertEqual(
            categorize(Diagnostic("expected one of `.`, `;`, `?` ... found keyword `let`", "f")),
            Category.MISSING_SEMICOLON)

    def test_uncategorized(self):
        self.assertIsNone(categorize(Diagnostic("some random error", "f", code="E9999")))


class TestHealRules(unittest.TestCase):
    def test_missing_semicolon_edit(self):
        src = b"let x = 1\nlet y = 2\n"
        edits = _plan_edits(src, [Diagnostic("expected `;`", "f", start_byte=9)], "rust", None)
        self.assertEqual(_apply_edits(src, edits), b"let x = 1;\nlet y = 2\n")

    def test_immutable_assignment_adds_mut(self):
        src = b"fn main(){ let x = 1; x = 2; }"
        d = Diagnostic("cannot assign twice to immutable variable `x`", "f", code="E0384")
        edits = _plan_edits(src, [d], "rust", None)
        self.assertEqual(_apply_edits(src, edits), b"fn main(){ let mut x = 1; x = 2; }")

    def test_immutable_only_targets_named_binding(self):
        src = b"fn main(){ let a = 1; let b = 2; b = 3; }"
        d = Diagnostic("cannot assign twice to immutable variable `b`", "f", code="E0384")
        edits = _plan_edits(src, [d], "rust", None)
        out = _apply_edits(src, edits).decode()
        self.assertIn("let mut b", out)
        self.assertNotIn("let mut a", out)

    def test_python_missing_import_uses_dag(self):
        with tempfile.TemporaryDirectory() as ws:
            os.makedirs(os.path.join(ws, "pkg"))
            Path(ws, "pkg", "util.py").write_text("def helper():\n    return 1\n")
            index = SymbolIndex.build(Path(ws))
            self.assertEqual(index.module_for("helper"), "pkg/util.py")
            src = b"x = helper()\n"
            d = Diagnostic('"helper" is not defined', "f")
            edits = _plan_edits(src, [d], "python", index)
            out = _apply_edits(src, edits).decode()
            self.assertTrue(out.startswith("from pkg.util import helper\n"))


class TestHealLoop(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_heal_then_success(self):
        f = Path(self.ws, "a.rs")
        f.write_text("fn main(){ let x = 1; x = 2; }\n")

        def build(path):
            if "let mut x" in path.read_text():
                return []
            return [Diagnostic("cannot assign twice to immutable variable `x`",
                               str(path), code="E0384")]

        report = heal_module(f, build, workspace=self.ws)
        self.assertTrue(report.success)
        self.assertEqual(report.attempts, 2)
        self.assertIn("immutable_assignment", report.applied)
        self.assertIn("let mut x", f.read_text())

    def test_rollback_on_unhealable(self):
        f = Path(self.ws, "b.rs")
        original = "fn main(){ let y = 1; }\n"
        f.write_text(original)
        bp = Path(self.ws, "blueprint.aero")
        bp.write_text('[system]\nname = "t"\n')

        def build(path):
            return [Diagnostic("mysterious failure", str(path), code="E9999")]

        report = heal_module(f, build, workspace=self.ws, blueprint_path=bp)
        self.assertFalse(report.success)
        self.assertTrue(report.rolled_back)
        self.assertEqual(f.read_text(), original)  # restored
        text = bp.read_text()
        self.assertIn("[self_healing]", text)
        self.assertIn("E9999", text)

    def test_budget_capped_at_three_builds(self):
        f = Path(self.ws, "c.rs")
        f.write_text("fn main(){ let z = 1 }\n")
        calls = {"n": 0}

        def build(path):
            calls["n"] += 1
            # Healable category, but never actually fixed -> keeps editing.
            return [Diagnostic("expected `;`", str(path),
                               start_byte=len(path.read_text()) - 3)]

        report = heal_module(f, build, workspace=self.ws)
        self.assertFalse(report.success)
        self.assertTrue(report.rolled_back)
        self.assertLessEqual(calls["n"], 3)
        self.assertLessEqual(report.attempts, 3)

    def test_blueprint_flag_idempotent(self):
        bp = Path(self.ws, "blueprint.aero")
        bp.write_text('[scaling]\nhierarchy_depth = 4\n')
        flag_healing_failure(bp, "m1.rs", "reason a", [Diagnostic("e", "f", code="E1")])
        flag_healing_failure(bp, "m2.rs", "reason b", [Diagnostic("e", "f", code="E2")])
        text = bp.read_text()
        self.assertEqual(text.count("[self_healing]"), 1)  # single table
        self.assertIn("m1.rs", text)
        self.assertIn("m2.rs", text)
        self.assertIn("[scaling]", text)  # other sections preserved
        from src.blueprint.loader import _toml
        parsed = _toml.loads(text)
        self.assertIn("self_healing", parsed)


@unittest.skipUnless(_has("rustc"), "rustc not available")
class TestRealRustc(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_real_mutability_heal(self):
        f = Path(self.ws, "m.rs")
        f.write_text("fn main(){ let x = 1; x = 2; let _ = x; }\n")
        report = heal_module(f, make_rust_build_fn(), workspace=self.ws)
        self.assertTrue(report.success)
        self.assertIn("let mut x", f.read_text())

    def test_real_semicolon_heal(self):
        f = Path(self.ws, "s.rs")
        f.write_text("fn main(){ let x = 1 let _ = x; }\n")
        report = heal_module(f, make_rust_build_fn(), workspace=self.ws)
        self.assertTrue(report.success)


if __name__ == "__main__":
    unittest.main()
