from __future__ import annotations

from .ast import (
    AssignStmt,
    Expr,
    FunctionDecl,
    IfStmt,
    LetStmt,
    Param,
    Program,
    RecordDecl,
    ReturnStmt,
    Stmt,
)
from .tokens import DoloSyntaxError, Token, tokenize


class Parser:
    def __init__(self, source: str):
        self.tokens = tokenize(source)
        self.index = 0

    def parse(self) -> Program:
        records: list[RecordDecl] = []
        functions: list[FunctionDecl] = []
        self._skip_newlines()
        while not self._at("EOF"):
            if self._match_value("record"):
                records.append(self._parse_record_after_keyword())
            elif self._match_value("fn"):
                functions.append(self._parse_function_after_keyword())
            else:
                self._fail("expected top-level record or fn")
            self._skip_newlines()
        return Program(tuple(records), tuple(functions))

    def _parse_record_after_keyword(self) -> RecordDecl:
        name = self._expect_kind("IDENT").value
        self._expect_value("{")
        fields: list[str] = []
        while not self._match_value("}"):
            fields.append(self._expect_kind("IDENT").value)
            if self._match_value(","):
                continue
            self._expect_value("}")
            break
        return RecordDecl(name, tuple(fields))

    def _parse_function_after_keyword(self) -> FunctionDecl:
        name = self._expect_kind("IDENT").value
        self._expect_value("(")
        params = self._parse_params()
        self._expect_value(")")
        self._expect_value("{")
        body = self._parse_block()
        return FunctionDecl(name, tuple(params), tuple(body))

    def _parse_params(self) -> list[Param]:
        params: list[Param] = []
        if self._peek_value(")"):
            return params
        while True:
            name = self._expect_kind("IDENT").value
            type_name = None
            if self._match_value(":"):
                type_name = self._expect_kind("IDENT").value
            params.append(Param(name, type_name))
            if not self._match_value(","):
                return params

    def _parse_block(self) -> list[Stmt]:
        body: list[Stmt] = []
        self._skip_newlines()
        while not self._match_value("}"):
            if self._at("EOF"):
                self._fail("unterminated block")
            body.append(self._parse_stmt())
            self._skip_newlines()
        return body

    def _parse_stmt(self) -> Stmt:
        if self._match_value("let"):
            name = self._expect_kind("IDENT").value
            self._expect_value("=")
            return LetStmt(name, self._expr_until_line())
        if self._match_value("return"):
            return ReturnStmt(self._expr_until_line())
        if self._match_value("if"):
            condition = self._expr_until_value("{")
            self._expect_value("{")
            then_body = tuple(self._parse_block())
            self._skip_newlines()
            else_body: tuple[Stmt, ...] = ()
            if self._match_value("else"):
                self._expect_value("{")
                else_body = tuple(self._parse_block())
            return IfStmt(condition, then_body, else_body)

        name = self._expect_kind("IDENT").value
        self._expect_value("=")
        return AssignStmt(name, self._expr_until_line())

    def _expr_until_line(self) -> Expr:
        collected: list[Token] = []
        depth = 0
        while True:
            token = self._peek()
            if token.kind == "EOF":
                break
            if token.value in ("(", "{"):
                depth += 1
            elif token.value in (")", "}"):
                if depth == 0:
                    break
                depth -= 1
            if depth == 0 and token.kind == "NEWLINE":
                break
            collected.append(self._advance())
        if not collected:
            self._fail("expected expression")
        return Expr(tuple(collected))

    def _expr_until_value(self, value: str) -> Expr:
        collected: list[Token] = []
        depth = 0
        while True:
            token = self._peek()
            if token.kind == "EOF":
                self._fail(f"expected {value!r}")
            if depth == 0 and token.value == value:
                break
            if token.value == "(":
                depth += 1
            elif token.value == ")":
                depth -= 1
            if token.kind != "NEWLINE":
                collected.append(token)
            self._advance()
        if not collected:
            self._fail("expected expression")
        return Expr(tuple(collected))

    def _skip_newlines(self) -> None:
        while self._at("NEWLINE"):
            self._advance()

    def _match_value(self, value: str) -> bool:
        if self._peek_value(value):
            self._advance()
            return True
        return False

    def _peek_value(self, value: str) -> bool:
        return self._peek().value == value

    def _expect_value(self, value: str) -> Token:
        if not self._peek_value(value):
            self._fail(f"expected {value!r}")
        return self._advance()

    def _expect_kind(self, kind: str) -> Token:
        if not self._at(kind):
            self._fail(f"expected {kind.lower()}")
        return self._advance()

    def _at(self, kind: str) -> bool:
        return self._peek().kind == kind

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def _fail(self, message: str) -> None:
        token = self._peek()
        raise DoloSyntaxError(f"line {token.line}, column {token.column}: {message}")


def parse_source(source: str) -> Program:
    return Parser(source).parse()
