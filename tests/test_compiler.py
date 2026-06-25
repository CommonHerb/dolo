import unittest
import subprocess
import sys
from pathlib import Path

from dolo.compiler import compile_source


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


if __name__ == "__main__":
    unittest.main()
