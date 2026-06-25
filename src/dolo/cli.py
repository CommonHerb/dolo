from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import compile_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dolo", description="Compile Dolo source to Herbert.")
    parser.add_argument("source", type=Path)
    args = parser.parse_args(argv)

    sys.stdout.write(compile_source(args.source.read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
