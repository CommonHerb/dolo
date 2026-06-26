import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

from dolo.compiler import compile_source
from dolo.tokens import DoloSyntaxError


ROOT = Path(__file__).resolve().parents[1]


class CompilerTests(unittest.TestCase):
    def test_record_field_access_lowers_to_tuple_index(self):
        source = """record Citizen { name, hunger }

fn hunger_of(c: Citizen) {
  return c.hunger
}
"""
        expected = """func hunger_of(c):
  return c.1
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_record_type_propagates_through_identifier_binding(self):
        source = """record Citizen { name, hunger }

fn hunger_of(c: Citizen) {
  let alias = c
  return alias.hunger
}
"""
        expected = """func hunger_of(c):
  let alias = c
  return alias.1
end
"""

        try:
            emitted = compile_source(source)
        except DoloSyntaxError as exc:
            self.fail(f"record type should propagate through identifier binding: {exc}")

        self.assertEqual(emitted, expected)

    def test_record_declaration_rejects_duplicate_field_names(self):
        source = """record Citizen { name, hunger, name }

fn main() {
  return 1
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 1, column 32: record Citizen repeats field 'name'",
        ):
            compile_source(source)

    def test_function_declaration_rejects_duplicate_parameter_names(self):
        source = """fn bad(x, x) {
  return x
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 1, column 11: function bad repeats parameter 'x'",
        ):
            compile_source(source)

    def test_record_declaration_rejects_duplicate_record_names(self):
        source = """record Citizen { name }
record Citizen { hunger }

fn main() {
  return 1
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 8: duplicate record Citizen",
        ):
            compile_source(source)

    def test_function_declaration_rejects_duplicate_function_names(self):
        source = """fn main() {
  return 1
}

fn main() {
  return 2
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 5, column 4: duplicate function main",
        ):
            compile_source(source)

    def test_function_parameter_annotation_must_name_a_record(self):
        source = """fn bad(c: Missing) {
  return c
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 1, column 11: unknown record annotation 'Missing'",
        ):
            compile_source(source)

    def test_assignment_target_must_already_be_bound(self):
        source = """fn bad() {
  spare = 1
  return spare
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 3: assignment target 'spare' is not bound",
        ):
            compile_source(source)

    def test_let_binding_must_be_new(self):
        source = """fn bad(x) {
  let x = 1
  return x
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 7: let binding 'x' is already bound",
        ):
            compile_source(source)

    def test_function_call_target_must_be_known(self):
        source = """fn bad() {
  return missing(1)
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unknown function call 'missing'",
        ):
            compile_source(source)

    def test_function_call_requires_declared_arity(self):
        source = """fn need_two(a, b) {
  return a
}
fn bad() {
  return need_two(1)
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 5, column 10: function need_two expects 2 arguments, got 1",
        ):
            compile_source(source)

    def test_expression_variable_must_be_bound(self):
        source = """fn bad() {
  return spare
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unknown variable 'spare'",
        ):
            compile_source(source)

    def test_observed_herbert_builtin_call_target_is_allowed(self):
        source = """fn same(a, b) {
  return equal(a, b)
}
"""
        expected = """func same(a, b):
  return equal(a, b)
end
"""

        try:
            emitted = compile_source(source)
        except DoloSyntaxError as exc:
            self.fail(f"observed Herbert builtin should be allowed: {exc}")

        self.assertEqual(emitted, expected)

    def test_record_constructor_and_if_else_lower_to_herbert(self):
        source = """record Citizen { name, hunger }

fn hunger_status() {
  let c = Citizen("Ada", 3)
  if c.hunger > 2 {
    return "hungry"
  } else {
    return "steady"
  }
}
"""
        expected = """func hunger_status():
  let c = ("Ada", 3)
  if c.1 > 2:
    return "hungry"
  else:
    return "steady"
  end
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_examples_compile_to_committed_herbert(self):
        for stem in ("citizen", "ledger"):
            source = (ROOT / "examples" / f"{stem}.dolo").read_text()
            expected = (ROOT / "tests" / "fixtures" / f"{stem}.herb").read_text()
            self.assertEqual(compile_source(source), expected)

    def test_executable_manifest_examples_have_main_and_goldens(self):
        manifest = ROOT / "tests" / "fixtures" / "executable_manifest.tsv"
        self.assertTrue(manifest.is_file(), "executable manifest is required")
        rows = [
            tuple(line.split("\t"))
            for line in manifest.read_text().splitlines()
            if line and not line.startswith("#")
        ]
        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(rows, sorted(rows), "executable manifest rows must be sorted")

        for source_rel, herb_rel, stdout_rel in rows:
            with self.subTest(source=source_rel):
                source_path = ROOT / source_rel
                herb_path = ROOT / herb_rel
                stdout_path = ROOT / stdout_rel
                self.assertTrue(source_path.is_file(), f"source missing: {source_rel}")
                self.assertTrue(herb_path.is_file(), f"Herbert golden missing: {herb_rel}")
                self.assertTrue(stdout_path.is_file(), f"stdout golden missing: {stdout_rel}")
                source = source_path.read_text()

                self.assertIn("fn main()", source)
                self.assertEqual(compile_source(source), herb_path.read_text())
                self.assertTrue(stdout_path.read_text().endswith("\n"))

    def test_all_examples_are_classified_for_execution(self):
        executable_manifest = (
            ROOT / "tests" / "fixtures" / "executable_manifest.tsv"
        )
        non_executable_manifest = (
            ROOT / "tests" / "fixtures" / "non_executable_examples.tsv"
        )
        self.assertTrue(
            non_executable_manifest.is_file(),
            "non-executable example manifest is required",
        )

        executable_rows = [
            tuple(line.split("\t"))
            for line in executable_manifest.read_text().splitlines()
            if line and not line.startswith("#")
        ]
        executable_sources = {row[0] for row in executable_rows}

        non_executable_rows = [
            tuple(line.split("\t"))
            for line in non_executable_manifest.read_text().splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual(
            non_executable_rows,
            sorted(non_executable_rows),
            "non-executable example rows must be sorted",
        )

        non_executable_sources = set()
        for row in non_executable_rows:
            self.assertEqual(
                len(row),
                2,
                f"non-executable example row must have source and reason: {row!r}",
            )
            source_rel, reason = row
            self.assertTrue(
                reason.strip(),
                f"non-executable example needs a reason: {source_rel}",
            )
            self.assertTrue(
                (ROOT / source_rel).is_file(), f"source missing: {source_rel}"
            )
            non_executable_sources.add(source_rel)

        self.assertFalse(
            executable_sources & non_executable_sources,
            "examples cannot be both executable and non-executable",
        )
        example_sources = {
            str(path.relative_to(ROOT))
            for path in sorted((ROOT / "examples").glob("*.dolo"))
        }
        self.assertEqual(
            example_sources,
            executable_sources | non_executable_sources,
        )

    def test_cli_emits_herbert_to_stdout(self):
        source_path = ROOT / "examples" / "citizen.dolo"
        expected = (ROOT / "tests" / "fixtures" / "citizen.herb").read_text()

        result = subprocess.run(
            [sys.executable, "-m", "dolo.cli", str(source_path)],
            check=True,
            env={"PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout, expected)

    def test_cli_reports_syntax_errors_without_python_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "bad.dolo"
            source_path.write_text("""fn bad() {
  return @
}
""")

            result = subprocess.run(
                [sys.executable, "-m", "dolo.cli", str(source_path)],
                env={"PYTHONPATH": str(ROOT / "src")},
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr,
            "dolo: line 2, column 10: unexpected character '@'\n",
        )
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_reports_missing_source_without_python_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "missing.dolo"

            result = subprocess.run(
                [sys.executable, "-m", "dolo.cli", str(source_path)],
                env={"PYTHONPATH": str(ROOT / "src")},
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr,
            f"dolo: {source_path}: No such file or directory\n",
        )
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_record_constructor_requires_exact_field_count(self):
        too_few = """record Citizen { name, hunger }

fn bad() {
  let c = Citizen("Ada")
  return c.hunger
}
"""
        too_many = """record Citizen { name, hunger }

fn bad() {
  let c = Citizen("Ada", 3, 99)
  return c.hunger
}
"""

        with self.assertRaisesRegex(DoloSyntaxError, "Citizen expects 2 fields, got 1"):
            compile_source(too_few)
        with self.assertRaisesRegex(DoloSyntaxError, "Citizen expects 2 fields, got 3"):
            compile_source(too_many)

    def test_record_constructor_arity_diagnostic_reports_column(self):
        source = """record Citizen { name, hunger }

fn bad() {
  let c = Citizen("Ada")
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 4, column 11: record Citizen expects 2 fields, got 1",
        ):
            compile_source(source)

    def test_unresolved_field_access_diagnostic_reports_target_column(self):
        source = """fn bad(c) {
  return c.hunger
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: cannot resolve record type for c.hunger",
        ):
            compile_source(source)

    def test_unknown_record_field_diagnostic_reports_field_column(self):
        source = """record Citizen { name, hunger }

fn bad(c: Citizen) {
  return c.coins
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 4, column 12: record Citizen has no field 'coins'",
        ):
            compile_source(source)

    def test_unclosed_expression_delimiter_reports_opening_column(self):
        source = """record Citizen { name, hunger }

fn bad() {
  let c = Citizen("Ada"
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 4, column 18: unterminated '\(' in expression",
        ):
            compile_source(source)

    def test_unclosed_expression_delimiter_at_eof_reports_opening_column(self):
        source = """fn bad() {
  return missing(1"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 17: unterminated '\(' in expression",
        ):
            compile_source(source)

    def test_unclosed_condition_delimiter_reports_opening_column(self):
        source = """fn bad() {
  if missing(1 {
    return 1
  }
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 13: unterminated '\(' in expression",
        ):
            compile_source(source)

    def test_unmatched_expression_closer_reports_closer_column(self):
        source = """fn bad(flag) {
  return flag)
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 14: unexpected '\)' in expression",
        ):
            compile_source(source)

    def test_unmatched_condition_closer_reports_closer_column(self):
        source = """fn bad(flag) {
  if flag) {
    return 1
  }
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unexpected '\)' in expression",
        ):
            compile_source(source)

    def test_bang_lowers_to_herbert_not(self):
        source = """fn ready(flag) {
  return !flag
}
"""
        expected = """func ready(flag):
  return not flag
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_unexpected_character_diagnostic_reports_line_and_column(self):
        source = """fn bad() {
  return @
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unexpected character '@'",
        ):
            compile_source(source)

    def test_unterminated_string_diagnostic_reports_start_line_and_column(self):
        source = """fn bad() {
  return "open
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unterminated string literal",
        ):
            compile_source(source)

    def test_unterminated_character_diagnostic_reports_start_line_and_column(self):
        source = """fn bad() {
  return 'x
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unterminated character literal",
        ):
            compile_source(source)

    def test_herbert_truth_harness_is_pinned(self):
        lock = ROOT / "HERBERT.lock"
        harness = ROOT / "scripts" / "verify_herbert_truth.sh"

        self.assertTrue(lock.is_file(), "Herbert target lock is required")
        lock_text = lock.read_text()
        self.assertIn(
            "HERBERT_COMMIT=e9dff2283113063f60fece453e9ab9eb16e7366a",
            lock_text,
        )
        self.assertIn(
            "HERBERT_SEED_SHA256=8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50",
            lock_text,
        )

        self.assertTrue(harness.is_file(), "Herbert truth harness is required")
        harness_text = harness.read_text()
        for required in ("a.out", "sha256", "x86_64"):
            self.assertIn(required, harness_text)

    def test_herbert_truth_harness_stages_seed_copy(self):
        harness = ROOT / "scripts" / "verify_herbert_truth.sh"
        harness_text = harness.read_text()

        self.assertIn('cp "$seed" "$compiler"', harness_text)
        self.assertIn('chmod +x "$compiler"', harness_text)
        self.assertNotIn('"$seed" <"$generated"', harness_text)

    def test_first_herbert_migration_candidate_is_manifested(self):
        manifest = ROOT / "tests" / "fixtures" / "herbert_migration_manifest.tsv"
        self.assertTrue(manifest.is_file(), "Herbert migration manifest is required")
        rows = [
            tuple(line.split("\t"))
            for line in manifest.read_text().splitlines()
            if line and not line.startswith("#")
        ]
        self.assertGreaterEqual(len(rows), 1)

        for source_rel, stdout_rel in rows:
            with self.subTest(source=source_rel):
                source_path = ROOT / source_rel
                stdout_path = ROOT / stdout_rel

                self.assertEqual(source_path.suffix, ".herb")
                self.assertIn("func main()", source_path.read_text())
                self.assertTrue(stdout_path.read_text().endswith("\n"))

    def test_herbert_truth_harness_runs_migration_candidates(self):
        harness = ROOT / "scripts" / "verify_herbert_truth.sh"

        self.assertIn("herbert_migration_manifest.tsv", harness.read_text())


if __name__ == "__main__":
    unittest.main()
