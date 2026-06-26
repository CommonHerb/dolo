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

    def test_field_access_requires_identifier_target_and_field(self):
        cases = (
            (
                """fn bad(x) {
  return x.
}
""",
                r"line 2, column 11: field access requires a field name",
            ),
            (
                """fn bad(x) {
  return .x
}
""",
                r"line 2, column 10: field access requires an identifier target",
            ),
            (
                """fn bad(x) {
  return x.(1)
}
""",
                r"line 2, column 11: field access requires a field name",
            ),
            (
                """record Pair { left, right }

fn bad() {
  return Pair(1, 2).left
}
""",
                r"line 4, column 20: field access requires an identifier target",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

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

    def test_record_declaration_requires_at_least_one_field(self):
        source = """record Empty { }

fn main() {
  return Empty()
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 1, column 8: record Empty must declare at least one field",
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

    def test_top_level_declaration_names_must_not_overlap(self):
        cases = (
            (
                """record Thing { value }

fn Thing() {
  return 1
}
""",
                r"line 3, column 4: duplicate top-level declaration Thing",
            ),
            (
                """fn Thing() {
  return 1
}

record Thing { value }
""",
                r"line 5, column 8: duplicate top-level declaration Thing",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_function_declaration_rejects_observed_herbert_builtin_names(self):
        cases = (
            (
                """fn length(value) {
  return value
}
""",
                r"line 1, column 4: function reuses observed Herbert built-in name 'length'",
            ),
            (
                """fn add(a, b) {
  return a + b
}
""",
                r"line 1, column 4: function reuses observed Herbert built-in name 'add'",
            ),
            (
                """fn new_array() {
  return 7
}
""",
                r"line 1, column 4: function reuses observed Herbert built-in name 'new_array'",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_main_function_must_take_no_parameters(self):
        source = """fn main(seed) {
  return seed
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 1, column 4: function 'main' must take zero parameters",
        ):
            compile_source(source)

    def test_functions_must_return_on_all_paths(self):
        cases = (
            (
                """fn helper() {
  let x = 1
}
""",
                r"line 1, column 4: function 'helper' may complete without returning",
            ),
            (
                """fn main() {
  let x = 1
}
""",
                r"line 1, column 4: function 'main' may complete without returning",
            ),
            (
                """fn main() {
  if true {
    return 1
  }
}
""",
                r"line 1, column 4: function 'main' may complete without returning",
            ),
            (
                """fn maybe(flag) {
  if flag {
    return 1
  }
}
""",
                r"line 1, column 4: function 'maybe' may complete without returning",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_if_else_return_in_both_arms_satisfies_function_return(self):
        source = """fn choose(flag) {
  if flag {
    return 1
  } else {
    return 2
  }
}
"""
        expected = """func choose(flag):
  if flag:
    return 1
  else:
    return 2
  end
end
"""

        self.assertEqual(compile_source(source), expected)

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

    def test_expression_keyword_must_be_literal(self):
        source = """fn bad() {
  return let
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: unexpected keyword 'let' in expression",
        ):
            compile_source(source)

    def test_assignment_operator_is_not_allowed_inside_expressions(self):
        cases = (
            (
                """fn bad(x) {
  return x = 1
}
""",
                r"line 2, column 12: unexpected assignment operator in expression",
            ),
            (
                """fn bad() {
  let x = 0
  let y = x = 1
  return y
}
""",
                r"line 3, column 13: unexpected assignment operator in expression",
            ),
            (
                """fn bad(flag) {
  if flag = true {
    return 1
  } else {
    return 0
  }
}
""",
                r"line 2, column 11: unexpected assignment operator in expression",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_binary_operators_require_operands(self):
        cases = (
            (
                """fn bad() {
  return 1 +
}
""",
                r"line 2, column 12: binary operator '\+' requires a right operand",
            ),
            (
                """fn bad() {
  return + 1
}
""",
                r"line 2, column 10: binary operator '\+' requires a left operand",
            ),
            (
                """fn bad() {
  return 1 + * 2
}
""",
                r"line 2, column 12: binary operator '\+' requires a right operand",
            ),
            (
                """fn bad(flag) {
  if flag && {
    return 1
  } else {
    return 0
  }
}
""",
                r"line 2, column 11: binary operator '&&' requires a right operand",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_prefix_not_is_allowed_in_expressions(self):
        source = """fn ok(flag) {
  return !flag
}
"""
        expected = """func ok(flag):
  return not flag
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_parenthesized_expressions_must_not_be_empty(self):
        source = """fn bad() {
  return ()
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 10: empty parenthesized expression is not implemented",
        ):
            compile_source(source)

    def test_expression_commas_require_values_on_both_sides(self):
        cases = (
            (
                """fn bad() {
  return (,1)
}
""",
                r"line 2, column 11: comma requires a preceding expression",
            ),
            (
                """fn bad() {
  return (1,)
}
""",
                r"line 2, column 12: comma requires a following expression",
            ),
            (
                """fn bad() {
  return (1,,2)
}
""",
                r"line 2, column 13: comma requires a preceding expression",
            ),
            (
                """fn f(x) {
  return x
}
fn bad() {
  return f(,1)
}
""",
                r"line 5, column 12: comma requires a preceding expression",
            ),
            (
                """fn f(x) {
  return x
}
fn bad() {
  return f(1,)
}
""",
                r"line 5, column 13: comma requires a following expression",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_zero_argument_calls_remain_valid_expressions(self):
        source = """fn ok() {
  return new_buffer()
}
"""
        expected = """func ok():
  return new_buffer()
end
"""

        self.assertEqual(compile_source(source), expected)

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

    def test_observed_herbert_builtin_call_requires_observed_arity(self):
        cases = (
            (
                """fn bad() {
  return length("abc", 1)
}
""",
                r"line 2, column 10: built-in length expects 1 argument, got 2",
            ),
            (
                """fn bad() {
  return index("abc")
}
""",
                r"line 2, column 10: built-in index expects 2 arguments, got 1",
            ),
            (
                """fn bad() {
  return equal("a")
}
""",
                r"line 2, column 10: built-in equal expects 2 arguments, got 1",
            ),
            (
                """fn bad() {
  return new_buffer(1)
}
""",
                r"line 2, column 10: built-in new_buffer expects 0 arguments, got 1",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_new_array_accepts_observed_herbert_type_expressions(self):
        source = """fn empty_counts() {
  return (count(new_array(int)), count(new_array(array(string))), count(new_array((int, bool))))
}
"""
        expected = """func empty_counts():
  return (count(new_array(int)), count(new_array(array(string))), count(new_array((int, bool))))
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_expression_formatting_keeps_space_before_group_after_comma(self):
        source = """fn shape() {
  return count(new_array(array((int, (bool, string)))))
}
"""
        expected = """func shape():
  return count(new_array(array((int, (bool, string)))))
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_new_array_type_argument_must_be_observed_herbert_type_expression(self):
        source = """fn bad() {
  return new_array(Missing)
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 20: unknown Herbert type 'Missing' in new_array argument",
        ):
            compile_source(source)

    def test_new_array_tuple_type_requires_multiple_fields(self):
        source = """fn bad() {
  return new_array((int))
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 20: Herbert tuple type in new_array argument "
            r"requires at least two fields",
        ):
            compile_source(source)

    def test_new_array_requires_one_herbert_type_argument(self):
        cases = (
            (
                """fn bad() {
  return new_array()
}
""",
                r"line 2, column 10: new_array expects one Herbert type argument, got 0",
            ),
            (
                """fn bad() {
  return new_array(int, string)
}
""",
                r"line 2, column 10: new_array expects one Herbert type argument, got 2",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_herbert_void_builtins_are_not_value_calls(self):
        cases = (
            (
                """fn bad(a) {
  return add(a, 1)
}
""",
                r"line 2, column 10: built-in add has no value; use a do statement",
            ),
            (
                """fn bad(b) {
  return append(b, 'h')
}
""",
                r"line 2, column 10: built-in append has no value; use a do statement",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_do_statement_emits_observed_no_value_herbert_builtin_calls(self):
        source = """fn mutate(items, label) {
  do add(items, 4)
  do append(label, 'x')
  return (count(items), freeze(label))
}
"""
        expected = """func mutate(items, label):
  do add(items, 4)
  do append(label, 'x')
  return (count(items), freeze(label))
end
"""

        self.assertEqual(compile_source(source), expected)

    def test_do_statement_rejects_value_builtin_calls(self):
        source = """fn bad() {
  do length("abc")
  return 0
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 6: do statement requires no-value Herbert built-in, got 'length'",
        ):
            compile_source(source)

    def test_do_statement_rejects_unknown_calls(self):
        source = """fn bad() {
  do missing(1)
  return 0
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 6: unknown do statement call 'missing'",
        ):
            compile_source(source)

    def test_do_statement_requires_one_whole_call(self):
        cases = (
            (
                """fn bad(items) {
  do items
  return 0
}
""",
                r"line 2, column 6: do statement requires a call",
            ),
            (
                """fn bad(items) {
  do add(items, 1) + 2
  return 0
}
""",
                r"line 2, column 20: do statement must contain exactly one call",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(DoloSyntaxError, expected):
                    compile_source(source)

    def test_do_statement_validates_no_value_builtin_arity(self):
        source = """fn bad(items) {
  do add(items)
  return 0
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 6: built-in add expects 2 arguments, got 1",
        ):
            compile_source(source)

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

    def test_text_builtin_example_compiles_to_committed_herbert(self):
        source_path = ROOT / "examples" / "text_probe.dolo"
        expected_path = ROOT / "tests" / "fixtures" / "text_probe.herb"
        self.assertTrue(source_path.is_file(), "text builtin example is required")
        self.assertTrue(expected_path.is_file(), "text builtin Herbert golden is required")
        source = source_path.read_text()
        expected = expected_path.read_text()

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

    def test_manifest_reader_rejects_malformed_rows(self):
        from dolo.manifests import ManifestError, read_manifest_rows

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "bad.tsv"
            manifest.write_text("examples/citizen.dolo\ttests/fixtures/citizen.herb\n")

            with self.assertRaisesRegex(
                ManifestError,
                r"bad.tsv:1: expected 3 tab-separated fields, got 2",
            ):
                read_manifest_rows(manifest, columns=3)

    def test_manifest_validator_accepts_repository_manifests(self):
        result = subprocess.run(
            [sys.executable, "-m", "dolo.manifests", "--root", str(ROOT), "verify"],
            env={"PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_manifest_validator_rejects_duplicate_source_rows(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "executable_manifest.tsv",
                "examples/a.dolo\ttests/fixtures/a.herb\ttests/fixtures/a.stdout\n"
                "examples/a.dolo\ttests/fixtures/a.herb\ttests/fixtures/a.stdout\n",
                None,
                None,
                r"executable_manifest.tsv: duplicate source examples/a.dolo",
            ),
            (
                "non_executable_examples.tsv",
                None,
                "examples/b.dolo\twaiting for list syntax\n"
                "examples/b.dolo\twaiting for list syntax\n",
                None,
                r"non_executable_examples.tsv: duplicate source examples/b.dolo",
            ),
            (
                "herbert_migration_manifest.tsv",
                None,
                None,
                "experiments/herbert/candidate.herb\ttests/fixtures/candidate.stdout\n"
                "experiments/herbert/candidate.herb\ttests/fixtures/candidate.stdout\n",
                r"herbert_migration_manifest.tsv: duplicate source "
                r"experiments/herbert/candidate.herb",
            ),
        )

        for (
            manifest_name,
            executable_rows,
            non_executable_rows,
            migration_rows,
            expected,
        ) in cases:
            with self.subTest(manifest=manifest_name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    (examples / "a.dolo").write_text("fn main() { return 1 }\n")
                    (examples / "b.dolo").write_text("fn listy() { return 1 }\n")
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")

                    (fixtures / "executable_manifest.tsv").write_text(
                        executable_rows
                        or (
                            "examples/a.dolo\ttests/fixtures/a.herb\t"
                            "tests/fixtures/a.stdout\n"
                        )
                    )
                    (fixtures / "non_executable_examples.tsv").write_text(
                        non_executable_rows
                        or "examples/b.dolo\twaiting for list syntax\n"
                    )
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        migration_rows
                        or (
                            "experiments/herbert/candidate.herb\t"
                            "tests/fixtures/candidate.stdout\n"
                        )
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_rejects_duplicate_output_targets(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "executable_manifest.tsv",
                (
                    "examples/a.dolo\ttests/fixtures/shared.herb\t"
                    "tests/fixtures/a.stdout\n"
                    "examples/b.dolo\ttests/fixtures/shared.herb\t"
                    "tests/fixtures/b.stdout\n"
                ),
                None,
                r"executable_manifest.tsv: duplicate Herbert golden "
                r"tests/fixtures/shared.herb",
            ),
            (
                "executable_manifest.tsv",
                (
                    "examples/a.dolo\ttests/fixtures/a.herb\t"
                    "tests/fixtures/shared.stdout\n"
                    "examples/b.dolo\ttests/fixtures/b.herb\t"
                    "tests/fixtures/shared.stdout\n"
                ),
                None,
                r"executable_manifest.tsv: duplicate stdout golden "
                r"tests/fixtures/shared.stdout",
            ),
            (
                "herbert_migration_manifest.tsv",
                None,
                (
                    "experiments/herbert/candidate_a.herb\t"
                    "tests/fixtures/shared.stdout\n"
                    "experiments/herbert/candidate_b.herb\t"
                    "tests/fixtures/shared.stdout\n"
                ),
                r"herbert_migration_manifest.tsv: duplicate stdout golden "
                r"tests/fixtures/shared.stdout",
            ),
        )

        for manifest_name, executable_rows, migration_rows, expected in cases:
            with self.subTest(manifest=manifest_name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    for name in ("a", "b"):
                        (examples / f"{name}.dolo").write_text(
                            """fn main() {
  return 1
}
"""
                        )
                        (fixtures / f"{name}.herb").write_text(
                            "func main():\n  return 1\nend\n"
                        )
                        (fixtures / f"{name}.stdout").write_text("1\n")
                    (fixtures / "shared.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "shared.stdout").write_text("1\n")
                    for name in ("candidate_a", "candidate_b"):
                        (experiments / f"{name}.herb").write_text(
                            "func main():\n  return 1\nend\n"
                        )
                    (fixtures / "executable_manifest.tsv").write_text(
                        executable_rows
                        or (
                            "examples/a.dolo\ttests/fixtures/a.herb\t"
                            "tests/fixtures/a.stdout\n"
                            "examples/b.dolo\ttests/fixtures/b.herb\t"
                            "tests/fixtures/b.stdout\n"
                        )
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        migration_rows
                        or (
                            "experiments/herbert/candidate_a.herb\t"
                            "tests/fixtures/a.stdout\n"
                            "experiments/herbert/candidate_b.herb\t"
                            "tests/fixtures/b.stdout\n"
                        )
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_executable_no_arg_main(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                """fn helper() {
  return 1
}
""",
                r"executable_manifest.tsv: examples/a.dolo must define no-argument fn main\(\)",
            ),
            (
                """fn main(seed) {
  return seed
}
""",
                r"executable_manifest.tsv: examples/a.dolo failed to parse: "
                r"line 1, column 4: function 'main' must take zero parameters",
            ),
        )

        for source, expected in cases:
            with self.subTest(source=source):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    (examples / "a.dolo").write_text(source)
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (fixtures / "executable_manifest.tsv").write_text(
                        "examples/a.dolo\ttests/fixtures/a.herb\t"
                        "tests/fixtures/a.stdout\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        "experiments/herbert/candidate.herb\t"
                        "tests/fixtures/candidate.stdout\n"
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_herbert_goldens_to_match_generated_output(
        self,
    ):
        from dolo.manifests import ManifestError, validate_repository_manifests

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "tests" / "fixtures"
            examples = root / "examples"
            experiments = root / "experiments" / "herbert"
            fixtures.mkdir(parents=True)
            examples.mkdir()
            experiments.mkdir(parents=True)
            (examples / "a.dolo").write_text(
                """fn main() {
  return 1
}
"""
            )
            (fixtures / "a.herb").write_text("func main():\n  return 2\nend\n")
            (fixtures / "a.stdout").write_text("1\n")
            (experiments / "candidate.herb").write_text(
                "func main():\n  return 1\nend\n"
            )
            (fixtures / "candidate.stdout").write_text("1\n")
            (fixtures / "executable_manifest.tsv").write_text(
                "examples/a.dolo\ttests/fixtures/a.herb\ttests/fixtures/a.stdout\n"
            )
            (fixtures / "non_executable_examples.tsv").write_text("")
            (fixtures / "herbert_migration_manifest.tsv").write_text(
                "experiments/herbert/candidate.herb\t"
                "tests/fixtures/candidate.stdout\n"
            )

            with self.assertRaisesRegex(
                ManifestError,
                r"executable_manifest.tsv: generated Herbert does not match "
                r"golden: examples/a.dolo -> tests/fixtures/a.herb",
            ):
                validate_repository_manifests(root)

    def test_manifest_validator_requires_executable_manifest_suffixes(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "examples/a.txt",
                "tests/fixtures/a.herb",
                "tests/fixtures/a.stdout",
                r"executable_manifest.tsv: source must be .dolo: examples/a.txt",
            ),
            (
                "examples/a.dolo",
                "tests/fixtures/a.txt",
                "tests/fixtures/a.stdout",
                r"executable_manifest.tsv: Herbert golden must be .herb: "
                r"tests/fixtures/a.txt",
            ),
            (
                "examples/a.dolo",
                "tests/fixtures/a.herb",
                "tests/fixtures/a.txt",
                r"executable_manifest.tsv: stdout golden must be .stdout: "
                r"tests/fixtures/a.txt",
            ),
        )

        for source_rel, herb_rel, stdout_rel, expected in cases:
            with self.subTest(row=(source_rel, herb_rel, stdout_rel)):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    (root / source_rel).write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (root / herb_rel).write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (root / stdout_rel).write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (fixtures / "executable_manifest.tsv").write_text(
                        f"{source_rel}\t{herb_rel}\t{stdout_rel}\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        "experiments/herbert/candidate.herb\t"
                        "tests/fixtures/candidate.stdout\n"
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_example_source_paths(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "src/a.dolo",
                "",
                r"executable_manifest.tsv: source must live under examples/: src/a.dolo",
            ),
            (
                "examples/a.dolo",
                "examples/b.txt\twaiting for syntax\n",
                r"non_executable_examples.tsv: source must be .dolo: examples/b.txt",
            ),
            (
                "examples/a.dolo",
                "notes/b.dolo\twaiting for syntax\n",
                r"non_executable_examples.tsv: source must live under examples/: notes/b.dolo",
            ),
        )

        for executable_source, non_executable_rows, expected in cases:
            with self.subTest(expected=expected):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    (root / executable_source).parent.mkdir(parents=True, exist_ok=True)
                    (root / executable_source).write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (examples / "a.dolo").write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (examples / "b.txt").write_text("fn helper() { return 1 }\n")
                    (root / "notes").mkdir(exist_ok=True)
                    (root / "notes" / "b.dolo").write_text(
                        "fn helper() { return 1 }\n"
                    )
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (fixtures / "executable_manifest.tsv").write_text(
                        f"{executable_source}\ttests/fixtures/a.herb\t"
                        "tests/fixtures/a.stdout\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text(
                        non_executable_rows
                    )
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        "experiments/herbert/candidate.herb\t"
                        "tests/fixtures/candidate.stdout\n"
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_owned_fixture_and_candidate_paths(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "tests/fixtures/a.herb",
                "tests/fixtures/a.stdout",
                "experiments/herbert/candidate.herb",
                "tests/fixtures/candidate.stdout",
                r"",
            ),
            (
                "examples/a.herb",
                "tests/fixtures/a.stdout",
                "experiments/herbert/candidate.herb",
                "tests/fixtures/candidate.stdout",
                r"executable_manifest.tsv: Herbert golden must live under tests/fixtures/: examples/a.herb",
            ),
            (
                "tests/fixtures/a.herb",
                "examples/a.stdout",
                "experiments/herbert/candidate.herb",
                "tests/fixtures/candidate.stdout",
                r"executable_manifest.tsv: stdout golden must live under tests/fixtures/: examples/a.stdout",
            ),
            (
                "tests/fixtures/a.herb",
                "tests/fixtures/a.stdout",
                "examples/candidate.herb",
                "tests/fixtures/candidate.stdout",
                r"herbert_migration_manifest.tsv: migration source must live under experiments/herbert/: examples/candidate.herb",
            ),
            (
                "tests/fixtures/a.herb",
                "tests/fixtures/a.stdout",
                "experiments/herbert/candidate.herb",
                "experiments/herbert/candidate.stdout",
                r"herbert_migration_manifest.tsv: stdout golden must live under tests/fixtures/: experiments/herbert/candidate.stdout",
            ),
        )

        for herb_rel, stdout_rel, migration_rel, migration_stdout_rel, expected in cases:
            with self.subTest(expected=expected or "valid"):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)

                    (examples / "a.dolo").write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    for relative_path, text in (
                        (herb_rel, "func main():\n  return 1\nend\n"),
                        (stdout_rel, "1\n"),
                        (migration_rel, "func main():\n  return 1\nend\n"),
                        (migration_stdout_rel, "1\n"),
                    ):
                        target = root / relative_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(text)

                    (fixtures / "executable_manifest.tsv").write_text(
                        f"examples/a.dolo\t{herb_rel}\t{stdout_rel}\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        f"{migration_rel}\t{migration_stdout_rel}\n"
                    )

                    if expected:
                        with self.assertRaisesRegex(ManifestError, expected):
                            validate_repository_manifests(root)
                    else:
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_stdout_goldens_to_end_with_newline(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "tests/fixtures/a.stdout",
                r"executable_manifest.tsv: stdout golden must end with newline: "
                r"tests/fixtures/a.stdout",
            ),
            (
                "tests/fixtures/candidate.stdout",
                r"herbert_migration_manifest.tsv: stdout golden must end with newline: "
                r"tests/fixtures/candidate.stdout",
            ),
        )

        for bad_stdout, expected in cases:
            with self.subTest(stdout=bad_stdout):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    (examples / "a.dolo").write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (root / bad_stdout).write_bytes(b"1")
                    (fixtures / "executable_manifest.tsv").write_text(
                        "examples/a.dolo\ttests/fixtures/a.herb\t"
                        "tests/fixtures/a.stdout\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        "experiments/herbert/candidate.herb\t"
                        "tests/fixtures/candidate.stdout\n"
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_migration_herbert_main(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "experiments/herbert/candidate.txt",
                "func main():\n  return 1\nend\n",
                r"herbert_migration_manifest.tsv: migration source must be .herb: "
                r"experiments/herbert/candidate.txt",
            ),
            (
                "experiments/herbert/candidate.herb",
                "func helper():\n  return 1\nend\n",
                r"herbert_migration_manifest.tsv: experiments/herbert/candidate.herb "
                r"must define func main\(\)",
            ),
        )

        for migration_source, migration_text, expected in cases:
            with self.subTest(source=migration_source):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    migration_path = root / migration_source
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    migration_path.parent.mkdir(parents=True, exist_ok=True)
                    (examples / "a.dolo").write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    migration_path.write_text(migration_text)
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (fixtures / "executable_manifest.tsv").write_text(
                        "examples/a.dolo\ttests/fixtures/a.herb\t"
                        "tests/fixtures/a.stdout\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        f"{migration_source}\ttests/fixtures/candidate.stdout\n"
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_requires_migration_candidate_note_links(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "candidate note does not mention source or stdout\n",
                r"herbert_migration_manifest.tsv: migration candidate note must mention "
                r"experiments/herbert/candidate.herb",
            ),
            (
                "candidate note mentions experiments/herbert/candidate.herb only\n",
                r"herbert_migration_manifest.tsv: migration candidate note must mention "
                r"tests/fixtures/candidate.stdout",
            ),
        )

        for note_text, expected in cases:
            with self.subTest(expected=expected):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    notes = root / "docs" / "migration-candidates"
                    fixtures.mkdir(parents=True)
                    examples.mkdir()
                    experiments.mkdir(parents=True)
                    notes.mkdir(parents=True)
                    (examples / "a.dolo").write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (notes / "0001-candidate.md").write_text(note_text)
                    (fixtures / "executable_manifest.tsv").write_text(
                        "examples/a.dolo\ttests/fixtures/a.herb\t"
                        "tests/fixtures/a.stdout\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text("")
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        "experiments/herbert/candidate.herb\t"
                        "tests/fixtures/candidate.stdout\n"
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

    def test_manifest_validator_rejects_orphaned_migration_candidate_notes(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "tests" / "fixtures"
            examples = root / "examples"
            experiments = root / "experiments" / "herbert"
            notes = root / "docs" / "migration-candidates"
            fixtures.mkdir(parents=True)
            examples.mkdir()
            experiments.mkdir(parents=True)
            notes.mkdir(parents=True)
            (examples / "a.dolo").write_text(
                """fn main() {
  return 1
}
"""
            )
            (fixtures / "a.herb").write_text("func main():\n  return 1\nend\n")
            (fixtures / "a.stdout").write_text("1\n")
            (experiments / "candidate.herb").write_text(
                "func main():\n  return 1\nend\n"
            )
            (fixtures / "candidate.stdout").write_text("1\n")
            (notes / "0001-candidate.md").write_text(
                "experiments/herbert/candidate.herb\n"
                "tests/fixtures/candidate.stdout\n"
            )
            (notes / "0002-orphan.md").write_text(
                "experiments/herbert/orphan.herb\n"
                "tests/fixtures/orphan.stdout\n"
            )
            (fixtures / "executable_manifest.tsv").write_text(
                "examples/a.dolo\ttests/fixtures/a.herb\t"
                "tests/fixtures/a.stdout\n"
            )
            (fixtures / "non_executable_examples.tsv").write_text("")
            (fixtures / "herbert_migration_manifest.tsv").write_text(
                "experiments/herbert/candidate.herb\t"
                "tests/fixtures/candidate.stdout\n"
            )

            with self.assertRaisesRegex(
                ManifestError,
                r"herbert_migration_manifest.tsv: migration candidate note "
                r"is not linked to a manifest source: "
                r"docs/migration-candidates/0002-orphan.md",
            ):
                validate_repository_manifests(root)

    def test_manifest_validator_requires_migration_stdout_suffix(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / "tests" / "fixtures"
            examples = root / "examples"
            experiments = root / "experiments" / "herbert"
            fixtures.mkdir(parents=True)
            examples.mkdir()
            experiments.mkdir(parents=True)
            (examples / "a.dolo").write_text(
                """fn main() {
  return 1
}
"""
            )
            (fixtures / "a.herb").write_text("func main():\n  return 1\nend\n")
            (fixtures / "a.stdout").write_text("1\n")
            (experiments / "candidate.herb").write_text(
                "func main():\n  return 1\nend\n"
            )
            (fixtures / "candidate.txt").write_text("1\n")
            (fixtures / "executable_manifest.tsv").write_text(
                "examples/a.dolo\ttests/fixtures/a.herb\t"
                "tests/fixtures/a.stdout\n"
            )
            (fixtures / "non_executable_examples.tsv").write_text("")
            (fixtures / "herbert_migration_manifest.tsv").write_text(
                "experiments/herbert/candidate.herb\ttests/fixtures/candidate.txt\n"
            )

            with self.assertRaisesRegex(
                ManifestError,
                r"herbert_migration_manifest.tsv: stdout golden must be .stdout: "
                r"tests/fixtures/candidate.txt",
            ):
                validate_repository_manifests(root)

    def test_manifest_validator_rejects_paths_outside_repository(self):
        from dolo.manifests import ManifestError, validate_repository_manifests

        cases = (
            (
                "examples/a.dolo",
                "../outside/a.herb",
                "tests/fixtures/a.stdout",
                "",
                "experiments/herbert/candidate.herb\t"
                "tests/fixtures/candidate.stdout\n",
                r"Herbert golden must be repository-relative: ../outside/a.herb",
            ),
            (
                "examples/a.dolo",
                "tests/fixtures/a.herb",
                "tests/fixtures/a.stdout",
                "",
                "experiments/herbert/candidate.herb\t../outside/candidate.stdout\n",
                r"migration stdout golden must be repository-relative: "
                r"../outside/candidate.stdout",
            ),
            (
                "examples/a.dolo",
                "tests/fixtures/a.herb",
                "tests/fixtures/a.stdout",
                "../outside/b.dolo\twaiting for list syntax\n",
                "experiments/herbert/candidate.herb\t"
                "tests/fixtures/candidate.stdout\n",
                r"source must be repository-relative: ../outside/b.dolo",
            ),
        )

        for (
            source_rel,
            herb_rel,
            stdout_rel,
            non_executable_rows,
            migration_rows,
            expected,
        ) in cases:
            with self.subTest(expected=expected):
                with tempfile.TemporaryDirectory() as tmp:
                    outer = Path(tmp)
                    root = outer / "repo"
                    outside = outer / "outside"
                    fixtures = root / "tests" / "fixtures"
                    examples = root / "examples"
                    experiments = root / "experiments" / "herbert"
                    fixtures.mkdir(parents=True)
                    examples.mkdir(parents=True)
                    experiments.mkdir(parents=True)
                    outside.mkdir()
                    (examples / "a.dolo").write_text(
                        """fn main() {
  return 1
}
"""
                    )
                    (fixtures / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "a.stdout").write_text("1\n")
                    (experiments / "candidate.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (fixtures / "candidate.stdout").write_text("1\n")
                    (outside / "a.herb").write_text(
                        "func main():\n  return 1\nend\n"
                    )
                    (outside / "b.dolo").write_text("fn listy() { return 1 }\n")
                    (outside / "candidate.stdout").write_text("1\n")
                    (fixtures / "executable_manifest.tsv").write_text(
                        f"{source_rel}\t{herb_rel}\t{stdout_rel}\n"
                    )
                    (fixtures / "non_executable_examples.tsv").write_text(
                        non_executable_rows
                    )
                    (fixtures / "herbert_migration_manifest.tsv").write_text(
                        migration_rows
                    )

                    with self.assertRaisesRegex(ManifestError, expected):
                        validate_repository_manifests(root)

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
  return c
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

    def test_else_if_reports_unsupported_form(self):
        source = """fn bad(flag) {
  if flag {
    return 1
  } else if false {
    return 2
  }
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 4, column 10: else if is not implemented; use else \{ if ... \}",
        ):
            compile_source(source)

    def test_elif_reports_unsupported_form(self):
        source = """fn bad(flag) {
  if flag {
    return 1
  } elif false {
    return 2
  }
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 4, column 5: elif is not implemented; use else \{ if ... \}",
        ):
            compile_source(source)

    def test_stray_else_reports_without_matching_if(self):
        source = """fn bad() {
  else {
    return 1
  }
}
"""

        with self.assertRaisesRegex(
            DoloSyntaxError,
            r"line 2, column 3: else without matching if",
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

    def test_ci_herbert_checkout_reads_lock(self):
        workflow = ROOT / ".github" / "workflows" / "check.yml"
        lock = ROOT / "HERBERT.lock"

        self.assertTrue(workflow.is_file(), "GitHub Actions check workflow is required")
        workflow_text = workflow.read_text()
        lock_text = lock.read_text()
        lock_commit = next(
            line.split("=", 1)[1]
            for line in lock_text.splitlines()
            if line.startswith("HERBERT_COMMIT=")
        )
        lock_repository_url = next(
            line.split("=", 1)[1]
            for line in lock_text.splitlines()
            if line.startswith("HERBERT_REPOSITORY=")
        )
        lock_repository = (
            lock_repository_url.removeprefix("https://github.com/")
            .removesuffix(".git")
        )

        self.assertIn("id: herbert-lock", workflow_text)
        self.assertIn('echo "commit=$HERBERT_COMMIT" >> "$GITHUB_OUTPUT"', workflow_text)
        self.assertIn('echo "repository=$herbert_repository" >> "$GITHUB_OUTPUT"', workflow_text)
        self.assertIn(
            "ref: ${{ steps.herbert-lock.outputs.commit }}",
            workflow_text,
        )
        self.assertIn(
            "repository: ${{ steps.herbert-lock.outputs.repository }}",
            workflow_text,
        )
        self.assertNotIn(f"ref: {lock_commit}", workflow_text)
        self.assertNotIn(f"repository: {lock_repository}", workflow_text)

    def test_herbert_migration_candidates_are_manifested(self):
        from dolo.manifests import read_manifest_rows

        manifest = ROOT / "tests" / "fixtures" / "herbert_migration_manifest.tsv"
        self.assertTrue(manifest.is_file(), "Herbert migration manifest is required")
        rows = read_manifest_rows(manifest, columns=2)
        self.assertGreaterEqual(len(rows), 1)
        self.assertTrue(
            {
                (
                    "experiments/herbert/array_mutation_candidate.herb",
                    "tests/fixtures/array_mutation_candidate.stdout",
                ),
                (
                    "experiments/herbert/record_field_index_candidate.herb",
                    "tests/fixtures/record_field_index_candidate.stdout",
                ),
            }.issubset(rows),
            "current Herbert migration candidates must stay manifested",
        )

        for source_rel, stdout_rel in rows:
            with self.subTest(source=source_rel):
                source_path = ROOT / source_rel
                stdout_path = ROOT / stdout_rel

                self.assertEqual(source_path.suffix, ".herb")
                self.assertIn("func main()", source_path.read_text())
                self.assertTrue(stdout_path.read_text().endswith("\n"))

    def test_herbert_truth_harness_runs_migration_candidates(self):
        harness = ROOT / "scripts" / "verify_herbert_truth.sh"
        harness_text = harness.read_text()

        self.assertIn("herbert_migration_manifest.tsv", harness_text)
        self.assertIn("python3 -m dolo.manifests", harness_text)

    def test_colima_truth_wrapper_keeps_profile_stopped_and_names_logs(self):
        wrapper = ROOT / "scripts" / "verify_herbert_truth_colima.sh"

        self.assertTrue(wrapper.is_file(), "Colima truth wrapper is required")
        wrapper_text = wrapper.read_text()

        self.assertIn('PROFILE="${PROFILE:-herbert-x86}"', wrapper_text)
        self.assertIn('HERBERT_DIR="${HERBERT_DIR:-../herbert}"', wrapper_text)
        self.assertIn('STOP_GRACE_SECONDS="${STOP_GRACE_SECONDS:-20}"', wrapper_text)
        self.assertIn('trap stop_profile EXIT', wrapper_text)
        self.assertIn("run_stop_command", wrapper_text)
        self.assertIn('label="colima stop -f"', wrapper_text)
        self.assertIn('stop_pid="$!"', wrapper_text)
        self.assertIn("timed out after", wrapper_text)
        self.assertIn('kill "$stop_pid"', wrapper_text)
        self.assertIn('kill -9 "$stop_pid"', wrapper_text)
        self.assertIn('colima stop -f "$PROFILE"', wrapper_text)
        self.assertIn("scripts/verify_herbert_truth.sh --herbert-dir", wrapper_text)
        self.assertIn("ha.stderr.log", wrapper_text)
        self.assertIn("serial.log", wrapper_text)


if __name__ == "__main__":
    unittest.main()
