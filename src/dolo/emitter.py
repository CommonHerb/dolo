from __future__ import annotations

from .ast import AssignStmt, Expr, FunctionDecl, IfStmt, LetStmt, Program, RecordDecl, ReturnStmt, Stmt
from .tokens import DoloSyntaxError, Token


class Emitter:
    def __init__(self, program: Program):
        self.program = program
        self.records = {record.name: record for record in program.records}
        self.functions = {function.name for function in program.functions}

    def emit(self) -> str:
        chunks = [self._emit_function(function) for function in self.program.functions]
        return "\n\n".join(chunks) + ("\n" if chunks else "")

    def _emit_function(self, function: FunctionDecl) -> str:
        record_types = {
            param.name: param.type_name
            for param in function.params
            if param.type_name in self.records
        }
        bindings = {param.name for param in function.params}
        params = ", ".join(param.name for param in function.params)
        lines = [f"func {function.name}({params}):"]
        self._emit_block(function.body, record_types, bindings, lines, 1)
        lines.append("end")
        return "\n".join(lines)

    def _emit_block(
        self,
        statements: tuple[Stmt, ...],
        record_types: dict[str, str | None],
        bindings: set[str],
        lines: list[str],
        indent: int,
    ) -> None:
        for stmt in statements:
            prefix = "  " * indent
            if isinstance(stmt, LetStmt):
                lines.append(f"{prefix}let {stmt.name} = {self._emit_expr(stmt.expr, record_types)}")
                bindings.add(stmt.name)
                record_types[stmt.name] = self._record_from_constructor(stmt.expr)
            elif isinstance(stmt, AssignStmt):
                if stmt.name not in bindings and stmt.name_token is not None:
                    raise DoloSyntaxError(
                        f"{_location(stmt.name_token)}: assignment target {stmt.name!r} is not bound"
                    )
                lines.append(f"{prefix}{stmt.name} = {self._emit_expr(stmt.expr, record_types)}")
                record_types[stmt.name] = self._record_from_constructor(stmt.expr)
            elif isinstance(stmt, ReturnStmt):
                lines.append(f"{prefix}return {self._emit_expr(stmt.expr, record_types)}")
            elif isinstance(stmt, IfStmt):
                lines.append(f"{prefix}if {self._emit_expr(stmt.condition, record_types)}:")
                self._emit_block(stmt.then_body, dict(record_types), set(bindings), lines, indent + 1)
                if stmt.else_body:
                    lines.append(f"{prefix}else:")
                    self._emit_block(
                        stmt.else_body,
                        dict(record_types),
                        set(bindings),
                        lines,
                        indent + 1,
                    )
                lines.append(f"{prefix}end")
            else:
                raise TypeError(f"unknown statement {stmt!r}")

    def _record_from_constructor(self, expr: Expr) -> str | None:
        tokens = expr.tokens
        if len(tokens) >= 2 and tokens[0].value in self.records and tokens[1].value == "(":
            return tokens[0].value
        return None

    def _emit_expr(self, expr: Expr, env: dict[str, str | None]) -> str:
        parts: list[str] = []
        i = 0
        while i < len(expr.tokens):
            token = expr.tokens[i]
            if (
                token.kind == "IDENT"
                and i + 2 < len(expr.tokens)
                and expr.tokens[i + 1].value == "."
                and expr.tokens[i + 2].kind == "IDENT"
            ):
                parts.append(self._emit_field_access(token, expr.tokens[i + 2], env))
                i += 3
                continue
            if token.kind == "IDENT" and token.value in self.records and self._next_value(expr, i, "("):
                self._validate_constructor(token, expr, i)
                i += 1
                continue
            if token.kind == "IDENT" and self._next_value(expr, i, "("):
                self._validate_call_target(token)
            value = _operator_value(token.value)
            parts.append(value)
            i += 1
        return _format_expr(parts)

    def _validate_constructor(self, token: Token, expr: Expr, index: int) -> None:
        record = self.records[token.value]
        got = self._constructor_arg_count(expr, index)
        want = len(record.fields)
        if got != want:
            raise DoloSyntaxError(
                f"{_location(token)}: record {record.name} expects {want} fields, got {got}"
            )

    def _constructor_arg_count(self, expr: Expr, index: int) -> int:
        depth = 0
        count = 0
        saw_argument = False
        for token in expr.tokens[index + 2 :]:
            if token.value == "(":
                depth += 1
                saw_argument = True
            elif token.value == ")":
                if depth == 0:
                    return count + 1 if saw_argument else 0
                depth -= 1
            elif token.value == "," and depth == 0:
                count += 1
            elif token.kind != "NEWLINE":
                saw_argument = True
        constructor = expr.tokens[index]
        raise DoloSyntaxError(f"line {constructor.line}: unterminated {constructor.value} constructor")

    def _emit_field_access(self, target: Token, field: Token, env: dict[str, str | None]) -> str:
        record_name = env.get(target.value)
        if record_name not in self.records:
            raise DoloSyntaxError(
                f"{_location(target)}: cannot resolve record type for {target.value}.{field.value}"
            )
        record = self.records[record_name]
        try:
            index = record.fields.index(field.value)
        except ValueError as exc:
            raise DoloSyntaxError(
                f"{_location(field)}: record {record.name} has no field {field.value!r}"
            ) from exc
        return f"{target.value}.{index}"

    def _validate_call_target(self, token: Token) -> None:
        if token.value in self.functions or token.value in HERBERT_BUILTINS:
            return
        raise DoloSyntaxError(f"{_location(token)}: unknown function call {token.value!r}")

    @staticmethod
    def _next_value(expr: Expr, index: int, value: str) -> bool:
        return index + 1 < len(expr.tokens) and expr.tokens[index + 1].value == value


def _format_expr(parts: list[str]) -> str:
    out = ""
    previous = ""
    operators = {"+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!=", "and", "or", "not", "="}
    for part in parts:
        if not out:
            out = part
        elif part in {")"}:
            out += part
        elif part == ",":
            out += part
        elif part == ".":
            out += part
        elif part == "(":
            out += part
        elif out.endswith("(") or out.endswith("."):
            out += part
        elif previous == ",":
            out += " " + part
        elif part in operators or previous in operators:
            out += " " + part
        else:
            out += " " + part
        previous = part
    return out


def _operator_value(value: str) -> str:
    if value == "&&":
        return "and"
    if value == "||":
        return "or"
    if value == "!":
        return "not"
    return value


def _location(token: Token) -> str:
    return f"line {token.line}, column {token.column}"


HERBERT_BUILTINS = frozenset(
    {
        "add",
        "append",
        "count",
        "equal",
        "freeze",
        "get",
        "index",
        "length",
        "new_array",
        "new_buffer",
    }
)


def emit_program(program: Program) -> str:
    return Emitter(program).emit()
