from __future__ import annotations

from .ast import AssignStmt, Expr, FunctionDecl, IfStmt, LetStmt, Program, RecordDecl, ReturnStmt, Stmt
from .tokens import DoloSyntaxError, Token


class Emitter:
    def __init__(self, program: Program):
        self.program = program
        self.records = {record.name: record for record in program.records}

    def emit(self) -> str:
        chunks = [self._emit_function(function) for function in self.program.functions]
        return "\n\n".join(chunks) + ("\n" if chunks else "")

    def _emit_function(self, function: FunctionDecl) -> str:
        env = {
            param.name: param.type_name
            for param in function.params
            if param.type_name in self.records
        }
        params = ", ".join(param.name for param in function.params)
        lines = [f"func {function.name}({params}):"]
        self._emit_block(function.body, env, lines, 1)
        lines.append("end")
        return "\n".join(lines)

    def _emit_block(
        self,
        statements: tuple[Stmt, ...],
        env: dict[str, str | None],
        lines: list[str],
        indent: int,
    ) -> None:
        for stmt in statements:
            prefix = "  " * indent
            if isinstance(stmt, LetStmt):
                lines.append(f"{prefix}let {stmt.name} = {self._emit_expr(stmt.expr, env)}")
                env[stmt.name] = self._record_from_constructor(stmt.expr)
            elif isinstance(stmt, AssignStmt):
                lines.append(f"{prefix}{stmt.name} = {self._emit_expr(stmt.expr, env)}")
                env[stmt.name] = self._record_from_constructor(stmt.expr)
            elif isinstance(stmt, ReturnStmt):
                lines.append(f"{prefix}return {self._emit_expr(stmt.expr, env)}")
            elif isinstance(stmt, IfStmt):
                lines.append(f"{prefix}if {self._emit_expr(stmt.condition, env)}:")
                self._emit_block(stmt.then_body, dict(env), lines, indent + 1)
                if stmt.else_body:
                    lines.append(f"{prefix}else:")
                    self._emit_block(stmt.else_body, dict(env), lines, indent + 1)
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
                i += 1
                continue
            value = "and" if token.value == "&&" else "or" if token.value == "||" else token.value
            parts.append(value)
            i += 1
        return _format_expr(parts)

    def _emit_field_access(self, target: Token, field: Token, env: dict[str, str | None]) -> str:
        record_name = env.get(target.value)
        if record_name not in self.records:
            raise DoloSyntaxError(
                f"line {target.line}: cannot resolve record type for {target.value}.{field.value}"
            )
        record = self.records[record_name]
        try:
            index = record.fields.index(field.value)
        except ValueError as exc:
            raise DoloSyntaxError(
                f"line {field.line}: record {record.name} has no field {field.value!r}"
            ) from exc
        return f"{target.value}.{index}"

    @staticmethod
    def _next_value(expr: Expr, index: int, value: str) -> bool:
        return index + 1 < len(expr.tokens) and expr.tokens[index + 1].value == value


def _format_expr(parts: list[str]) -> str:
    out = ""
    previous = ""
    operators = {"+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!=", "and", "or", "="}
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


def emit_program(program: Program) -> str:
    return Emitter(program).emit()
