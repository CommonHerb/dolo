from __future__ import annotations

from .ast import (
    AssignStmt,
    DoStmt,
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
from .herbert_surface import HERBERT_BUILTINS
from .tokens import DoloSyntaxError, Token, tokenize


CLOSING_DELIMITERS = {")": "(", "}": "{"}


class Parser:
    def __init__(self, source: str):
        self.tokens = tokenize(source)
        self.index = 0
        self.record_names: set[str] = set()
        self.function_names: set[str] = set()

    def parse(self) -> Program:
        records: list[RecordDecl] = []
        functions: list[FunctionDecl] = []
        self._skip_newlines()
        if self._at("EOF"):
            self._fail("source must contain at least one top-level record or fn")
        while not self._at("EOF"):
            if self._match_value("record"):
                records.append(self._parse_record_after_keyword())
            elif self._match_value("fn"):
                functions.append(self._parse_function_after_keyword())
            else:
                self._fail("expected top-level record or fn")
            self._skip_newlines()
        program = Program(tuple(records), tuple(functions))
        self._validate_record_annotations(program)
        return program

    def _parse_record_after_keyword(self) -> RecordDecl:
        name_token = self._expect_declaration_name("record")
        name = name_token.value
        if name in self.record_names:
            self._fail_at(name_token, f"duplicate record {name}")
        if name in self.function_names:
            self._fail_at(name_token, f"duplicate top-level declaration {name}")
        self.record_names.add(name)
        self._expect_value("{")
        fields: list[str] = []
        seen_fields: set[str] = set()
        while not self._match_value("}"):
            if self._peek_value(","):
                self._fail(f"record {name} field list expects a field name")
            field = self._expect_kind("IDENT")
            if field.value in seen_fields:
                self._fail_at(field, f"record {name} repeats field {field.value!r}")
            fields.append(field.value)
            seen_fields.add(field.value)
            if self._peek_value(","):
                comma = self._advance()
                if self._peek_value("}"):
                    self._fail_at(
                        comma,
                        f"record {name} field list cannot end with ','",
                    )
                continue
            self._expect_value("}")
            break
        if not fields:
            self._fail_at(name_token, f"record {name} must declare at least one field")
        return RecordDecl(name, tuple(fields))

    def _parse_function_after_keyword(self) -> FunctionDecl:
        name_token = self._expect_declaration_name("function")
        name = name_token.value
        if name in self.function_names:
            self._fail_at(name_token, f"duplicate function {name}")
        if name in self.record_names:
            self._fail_at(name_token, f"duplicate top-level declaration {name}")
        if name in HERBERT_BUILTINS:
            self._fail_at(
                name_token,
                f"function reuses observed Herbert built-in name {name!r}",
            )
        self.function_names.add(name)
        self._expect_value("(")
        params = self._parse_params(name)
        if name == "main" and params:
            self._fail_at(name_token, "function 'main' must take zero parameters")
        self._expect_value(")")
        self._expect_value("{")
        body = self._parse_block()
        if not _block_guarantees_return(tuple(body)):
            self._fail_at(
                name_token,
                f"function {name!r} may complete without returning",
            )
        return FunctionDecl(name, tuple(params), tuple(body))

    def _expect_declaration_name(self, kind: str) -> Token:
        if not self._at("IDENT"):
            self._fail(f"{kind} declaration expects a name")
        return self._advance()

    def _parse_params(self, function_name: str) -> list[Param]:
        params: list[Param] = []
        seen_params: set[str] = set()
        if self._peek_value(")"):
            return params
        while True:
            if self._peek_value(","):
                self._fail(
                    f"function {function_name} parameter list expects a parameter name"
                )
            name_token = self._expect_kind("IDENT")
            name = name_token.value
            if name in seen_params:
                self._fail_at(name_token, f"function {function_name} repeats parameter {name!r}")
            type_name = None
            type_token = None
            if self._match_value(":"):
                if not self._at("IDENT"):
                    self._fail(
                        f"function {function_name} parameter {name} "
                        "annotation expects a record name"
                    )
                type_token = self._advance()
                type_name = type_token.value
            params.append(Param(name, type_name, type_token))
            seen_params.add(name)
            if not self._peek_value(","):
                return params
            comma = self._advance()
            if self._peek_value(")"):
                self._fail_at(
                    comma,
                    f"function {function_name} parameter list cannot end with ','",
                )

    def _validate_record_annotations(self, program: Program) -> None:
        for function in program.functions:
            for param in function.params:
                if (
                    param.type_name is not None
                    and param.type_name not in self.record_names
                    and param.type_token is not None
                ):
                    self._fail_at(param.type_token, f"unknown record annotation {param.type_name!r}")

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
            if not self._at("IDENT"):
                self._fail("let statement expects a binding name")
            name_token = self._expect_kind("IDENT")
            name = name_token.value
            self._expect_value("=")
            return LetStmt(name, self._expr_until_line(), name_token)
        if self._match_value("do"):
            return DoStmt(self._expr_until_line())
        if self._match_value("return"):
            return ReturnStmt(self._expr_until_line())
        if self._match_value("if"):
            condition = self._expr_until_value("{")
            self._expect_value("{")
            then_body = tuple(self._parse_block())
            self._skip_newlines()
            else_body: tuple[Stmt, ...] = ()
            if self._match_value("else"):
                if self._peek_value("if"):
                    self._fail_at(
                        self._peek(),
                        "else if is not implemented; use else { if ... }",
                    )
                self._expect_value("{")
                else_body = tuple(self._parse_block())
            return IfStmt(condition, then_body, else_body)

        if self._peek_value("elif"):
            self._fail_at(
                self._peek(),
                "elif is not implemented; use else { if ... }",
            )

        if self._peek_value("else"):
            self._fail_at(self._peek(), "else without matching if")

        name_token = self._expect_kind("IDENT")
        name = name_token.value
        self._expect_value("=")
        return AssignStmt(name, self._expr_until_line(), name_token)

    def _expr_until_line(self) -> Expr:
        collected: list[Token] = []
        openers: list[Token] = []
        while True:
            token = self._peek()
            if token.kind == "EOF":
                if openers:
                    opener = openers[-1]
                    self._fail_at(opener, f"unterminated {opener.value!r} in expression")
                break
            if token.kind == "NEWLINE":
                if not openers:
                    break
                opener = openers[-1]
                self._fail_at(opener, f"unterminated {opener.value!r} in expression")
            if token.value in ("(", "{"):
                openers.append(token)
            elif token.value in CLOSING_DELIMITERS:
                if (
                    not openers
                    or openers[-1].value != CLOSING_DELIMITERS[token.value]
                ):
                    self._fail_at(token, f"unexpected {token.value!r} in expression")
                openers.pop()
            collected.append(self._advance())
        if not collected:
            self._fail("expected expression")
        return Expr(tuple(collected))

    def _expr_until_value(self, value: str) -> Expr:
        collected: list[Token] = []
        openers: list[Token] = []
        while True:
            token = self._peek()
            if token.kind == "EOF":
                if openers:
                    opener = openers[-1]
                    self._fail_at(opener, f"unterminated {opener.value!r} in expression")
                self._fail(f"expected {value!r}")
            if token.value == value:
                if openers:
                    opener = openers[-1]
                    self._fail_at(opener, f"unterminated {opener.value!r} in expression")
                break
            if token.value == "(":
                openers.append(token)
            elif token.value in CLOSING_DELIMITERS:
                if (
                    not openers
                    or openers[-1].value != CLOSING_DELIMITERS[token.value]
                ):
                    self._fail_at(token, f"unexpected {token.value!r} in expression")
                openers.pop()
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
        self._fail_at(token, message)

    @staticmethod
    def _fail_at(token: Token, message: str) -> None:
        raise DoloSyntaxError(f"line {token.line}, column {token.column}: {message}")


def parse_source(source: str) -> Program:
    return Parser(source).parse()


def _block_guarantees_return(statements: tuple[Stmt, ...]) -> bool:
    for stmt in statements:
        if _stmt_guarantees_return(stmt):
            return True
    return False


def _stmt_guarantees_return(stmt: Stmt) -> bool:
    if isinstance(stmt, ReturnStmt):
        return True
    if isinstance(stmt, IfStmt):
        return bool(stmt.else_body) and _block_guarantees_return(
            stmt.then_body
        ) and _block_guarantees_return(stmt.else_body)
    return False
