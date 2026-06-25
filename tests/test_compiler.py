import unittest
import subprocess
import sys
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

        for source_rel, herb_rel, stdout_rel in rows:
            with self.subTest(source=source_rel):
                source_path = ROOT / source_rel
                herb_path = ROOT / herb_rel
                stdout_path = ROOT / stdout_rel
                source = source_path.read_text()

                self.assertIn("fn main()", source)
                self.assertEqual(compile_source(source), herb_path.read_text())
                self.assertTrue(stdout_path.read_text().endswith("\n"))

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


if __name__ == "__main__":
    unittest.main()
