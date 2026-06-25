from __future__ import annotations

from .emitter import emit_program
from .parser import parse_source


def compile_source(source: str) -> str:
    """Compile Dolo source into the current Herbert target subset."""
    return emit_program(parse_source(source))
