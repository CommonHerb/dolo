from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import compile_source
from .tokens import DoloSyntaxError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dolo", description="Compile Dolo source to Herbert.")
    parser.add_argument("source", type=Path)
    args = parser.parse_args(argv)

    try:
        sys.stdout.write(compile_source(args.source.read_text()))
        return 0
    except DoloSyntaxError as exc:
        print(f"dolo: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        detail = exc.strerror or str(exc)
        print(f"dolo: {args.source}: {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
