from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int


class DoloSyntaxError(ValueError):
    pass


KEYWORDS = {"record", "fn", "let", "return", "if", "else", "true", "false"}
TWO_CHAR_OPS = {"==", "!=", "<=", ">=", "&&", "||"}
ONE_CHAR = set("{}(),.:+-*/%<>=!")


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1

    def add(kind: str, value: str, start_line: int, start_column: int) -> None:
        tokens.append(Token(kind, value, start_line, start_column))

    while i < len(source):
        ch = source[i]
        if ch in " \t\r":
            i += 1
            column += 1
            continue
        if ch == "\n":
            add("NEWLINE", "\n", line, column)
            i += 1
            line += 1
            column = 1
            continue
        if ch == "#":
            while i < len(source) and source[i] != "\n":
                i += 1
                column += 1
            continue
        if ch.isalpha() or ch == "_":
            start = i
            start_column = column
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
                column += 1
            value = source[start:i]
            kind = "KEYWORD" if value in KEYWORDS else "IDENT"
            add(kind, value, line, start_column)
            continue
        if ch.isdigit():
            start = i
            start_column = column
            while i < len(source) and source[i].isdigit():
                i += 1
                column += 1
            add("NUMBER", source[start:i], line, start_column)
            continue
        if ch in ('"', "'"):
            quote = ch
            literal_name = "string" if quote == '"' else "character"
            start = i
            start_line = line
            start_column = column
            i += 1
            column += 1
            escaped = False
            while i < len(source):
                cur = source[i]
                if cur == "\n":
                    raise DoloSyntaxError(
                        f"line {start_line}, column {start_column}: unterminated {literal_name} literal"
                    )
                i += 1
                column += 1
                if escaped:
                    escaped = False
                elif cur == "\\":
                    escaped = True
                elif cur == quote:
                    kind = "STRING" if quote == '"' else "CHAR"
                    add(kind, source[start:i], start_line, start_column)
                    break
            else:
                raise DoloSyntaxError(
                    f"line {start_line}, column {start_column}: unterminated {literal_name} literal"
                )
            continue
        two = source[i : i + 2]
        if two in TWO_CHAR_OPS:
            add("OP", two, line, column)
            i += 2
            column += 2
            continue
        if ch in ONE_CHAR:
            kind = "PUNCT" if ch in "{}(),.:" else "OP"
            add(kind, ch, line, column)
            i += 1
            column += 1
            continue
        raise DoloSyntaxError(f"line {line}, column {column}: unexpected character {ch!r}")

    tokens.append(Token("EOF", "", line, column))
    return tokens
