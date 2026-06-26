from __future__ import annotations

from dataclasses import dataclass

from .ast import (
    AssignStmt,
    DoStmt,
    Expr,
    FunctionDecl,
    IfStmt,
    LetStmt,
    Program,
    RecordDecl,
    ReturnStmt,
    Stmt,
)
from .herbert_surface import (
    DOLO_BOOLEAN_OPERATOR_LOWERINGS,
    HERBERT_BUILTIN_ARITIES,
    HERBERT_BUILTINS,
    HERBERT_TYPE_NAMES,
    HERBERT_VALUE_BUILTINS,
    HERBERT_VOID_BUILTINS,
)
from .tokens import DoloSyntaxError, Token


@dataclass
class EmitContext:
    record_types: dict[str, str | None]
    bindings: set[str]

    def branch(self) -> EmitContext:
        return EmitContext(dict(self.record_types), set(self.bindings))


class Emitter:
    def __init__(self, program: Program):
        self.program = program
        self.records = {record.name: record for record in program.records}
        self.functions = {function.name for function in program.functions}
        self.function_arities = {
            function.name: len(function.params)
            for function in program.functions
        }

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
        context = EmitContext(record_types, bindings)
        params = ", ".join(param.name for param in function.params)
        lines = [f"func {function.name}({params}):"]
        self._emit_block(function.body, context, lines, 1)
        lines.append("end")
        return "\n".join(lines)

    def _emit_block(
        self,
        statements: tuple[Stmt, ...],
        context: EmitContext,
        lines: list[str],
        indent: int,
    ) -> None:
        for stmt in statements:
            prefix = "  " * indent
            if isinstance(stmt, LetStmt):
                if stmt.name in context.bindings and stmt.name_token is not None:
                    raise DoloSyntaxError(
                        f"{_location(stmt.name_token)}: let binding {stmt.name!r} is already bound"
                    )
                lines.append(f"{prefix}let {stmt.name} = {self._emit_expr(stmt.expr, context)}")
                context.bindings.add(stmt.name)
                context.record_types[stmt.name] = self._record_from_expr(stmt.expr, context)
            elif isinstance(stmt, AssignStmt):
                if stmt.name not in context.bindings and stmt.name_token is not None:
                    raise DoloSyntaxError(
                        f"{_location(stmt.name_token)}: assignment target {stmt.name!r} is not bound"
                    )
                lines.append(f"{prefix}{stmt.name} = {self._emit_expr(stmt.expr, context)}")
                context.record_types[stmt.name] = self._record_from_expr(stmt.expr, context)
            elif isinstance(stmt, DoStmt):
                lines.append(f"{prefix}do {self._emit_do_expr(stmt.expr, context)}")
            elif isinstance(stmt, ReturnStmt):
                lines.append(f"{prefix}return {self._emit_expr(stmt.expr, context)}")
            elif isinstance(stmt, IfStmt):
                lines.append(f"{prefix}if {self._emit_expr(stmt.condition, context)}:")
                self._emit_block(stmt.then_body, context.branch(), lines, indent + 1)
                if stmt.else_body:
                    lines.append(f"{prefix}else:")
                    self._emit_block(stmt.else_body, context.branch(), lines, indent + 1)
                lines.append(f"{prefix}end")
            else:
                raise TypeError(f"unknown statement {stmt!r}")

    def _record_from_expr(self, expr: Expr, context: EmitContext) -> str | None:
        tokens = expr.tokens
        if len(tokens) >= 2 and tokens[0].value in self.records and tokens[1].value == "(":
            return tokens[0].value
        if len(tokens) == 1 and tokens[0].kind == "IDENT":
            return context.record_types.get(tokens[0].value)
        return None

    def _emit_expr(
        self,
        expr: Expr,
        context: EmitContext,
        *,
        allowed_void_call_indexes: frozenset[int] = frozenset(),
    ) -> str:
        parts: list[str] = []
        new_array_type_indexes = self._new_array_type_indexes(expr)
        self._validate_expression_shape(expr, new_array_type_indexes)
        i = 0
        while i < len(expr.tokens):
            token = expr.tokens[i]
            if i in new_array_type_indexes:
                parts.append(token.value)
                i += 1
                continue
            if token.kind == "KEYWORD" and token.value not in EXPRESSION_KEYWORDS:
                raise DoloSyntaxError(
                    f"{_location(token)}: unexpected keyword {token.value!r} in expression"
                )
            if token.value in INFIX_OPERATORS:
                self._validate_infix_operator(expr, i)
            if (
                token.kind == "IDENT"
                and i + 2 < len(expr.tokens)
                and expr.tokens[i + 1].value == "."
                and expr.tokens[i + 2].kind == "IDENT"
            ):
                parts.append(self._emit_field_access(token, expr.tokens[i + 2], context.record_types))
                i += 3
                continue
            if token.value == "=":
                raise DoloSyntaxError(
                    f"{_location(token)}: unexpected assignment operator in expression"
                )
            if token.kind == "IDENT" and token.value in self.records and self._next_value(expr, i, "("):
                self._validate_constructor(token, expr, i)
                i += 1
                continue
            if token.kind == "IDENT" and self._next_value(expr, i, "("):
                self._validate_call_target(
                    token,
                    allow_void_call=i in allowed_void_call_indexes,
                )
                self._validate_call_arity(token, expr, i)
            elif token.kind == "IDENT":
                self._validate_variable_reference(token, context)
            value = _operator_value(token.value)
            parts.append(value)
            i += 1
        return _format_expr(parts)

    def _emit_do_expr(self, expr: Expr, context: EmitContext) -> str:
        call = expr.tokens[0]
        if call.kind != "IDENT" or not self._next_value(expr, 0, "("):
            raise DoloSyntaxError(f"{_location(call)}: do statement requires a call")
        if call.value in self.functions:
            raise DoloSyntaxError(
                f"{_location(call)}: Dolo function {call.value!r} cannot be used as a do statement"
            )
        if call.value in HERBERT_VALUE_BUILTINS:
            raise DoloSyntaxError(
                f"{_location(call)}: do statement requires no-value Herbert built-in, got {call.value!r}"
            )
        if call.value not in HERBERT_VOID_BUILTINS:
            raise DoloSyntaxError(f"{_location(call)}: unknown do statement call {call.value!r}")
        close_index = self._call_close_index(expr, 0)
        if close_index != len(expr.tokens) - 1:
            token = expr.tokens[close_index + 1]
            raise DoloSyntaxError(
                f"{_location(token)}: do statement must contain exactly one call"
            )
        return self._emit_expr(
            expr,
            context,
            allowed_void_call_indexes=frozenset({0}),
        )

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

    def _new_array_type_indexes(self, expr: Expr) -> set[int]:
        indexes: set[int] = set()
        i = 0
        while i < len(expr.tokens):
            token = expr.tokens[i]
            if token.kind == "IDENT" and token.value == "new_array" and self._next_value(expr, i, "("):
                if token.value in self.functions:
                    i += 1
                    continue
                spans = self._call_argument_spans(expr, i)
                if len(spans) != 1:
                    raise DoloSyntaxError(
                        f"{_location(token)}: new_array expects one Herbert type argument, "
                        f"got {len(spans)}"
                    )
                start, end = spans[0]
                self._validate_herbert_type_expr(expr.tokens, start, end)
                indexes.update(range(start, end))
                i = self._call_close_index(expr, i) + 1
                continue
            i += 1
        return indexes

    def _call_argument_spans(self, expr: Expr, index: int) -> list[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        depth = 0
        start = index + 2
        for i, token in enumerate(expr.tokens[index + 2 :], start=index + 2):
            if token.value == "(":
                depth += 1
            elif token.value == ")":
                if depth == 0:
                    if start != i or spans:
                        spans.append((start, i))
                    return spans
                depth -= 1
            elif token.value == "," and depth == 0:
                spans.append((start, i))
                start = i + 1
        call = expr.tokens[index]
        raise DoloSyntaxError(f"{_location(call)}: unterminated {call.value} call")

    def _call_close_index(self, expr: Expr, index: int) -> int:
        depth = 0
        for i, token in enumerate(expr.tokens[index + 2 :], start=index + 2):
            if token.value == "(":
                depth += 1
            elif token.value == ")":
                if depth == 0:
                    return i
                depth -= 1
        call = expr.tokens[index]
        raise DoloSyntaxError(f"{_location(call)}: unterminated {call.value} call")

    def _validate_herbert_type_expr(
        self,
        tokens: tuple[Token, ...],
        start: int,
        end: int,
    ) -> None:
        if start >= end:
            token = tokens[start - 1] if start > 0 else tokens[0]
            raise DoloSyntaxError(
                f"{_location(token)}: expected Herbert type expression in new_array argument"
            )
        next_index = self._consume_herbert_type_expr(tokens, start, end)
        if next_index != end:
            token = tokens[next_index]
            raise DoloSyntaxError(
                f"{_location(token)}: expected end of Herbert type expression in new_array argument"
            )

    def _consume_herbert_type_expr(
        self,
        tokens: tuple[Token, ...],
        index: int,
        end: int,
    ) -> int:
        if index >= end:
            token = tokens[end - 1] if end > 0 else tokens[0]
            raise DoloSyntaxError(
                f"{_location(token)}: expected Herbert type expression in new_array argument"
            )
        token = tokens[index]
        if token.kind == "IDENT":
            if token.value in HERBERT_TYPE_NAMES:
                return index + 1
            if token.value == "array":
                if index + 1 >= end or tokens[index + 1].value != "(":
                    raise DoloSyntaxError(
                        f"{_location(token)}: array type expects one Herbert type argument"
                    )
                next_index = self._consume_herbert_type_expr(tokens, index + 2, end)
                if next_index >= end or tokens[next_index].value != ")":
                    raise DoloSyntaxError(
                        f"{_location(token)}: array type expects one Herbert type argument"
                    )
                return next_index + 1
            raise DoloSyntaxError(
                f"{_location(token)}: unknown Herbert type {token.value!r} in new_array argument"
            )
        if token.value == "(":
            return self._consume_herbert_tuple_type(tokens, index, end)
        raise DoloSyntaxError(
            f"{_location(token)}: expected Herbert type expression in new_array argument"
        )

    def _consume_herbert_tuple_type(
        self,
        tokens: tuple[Token, ...],
        index: int,
        end: int,
    ) -> int:
        next_index = index + 1
        if next_index >= end:
            token = tokens[index]
            raise DoloSyntaxError(
                f"{_location(token)}: unterminated Herbert tuple type in new_array argument"
            )
        field_count = 0
        while True:
            next_index = self._consume_herbert_type_expr(tokens, next_index, end)
            field_count += 1
            if next_index >= end:
                token = tokens[index]
                raise DoloSyntaxError(
                    f"{_location(token)}: unterminated Herbert tuple type in new_array argument"
                )
            if tokens[next_index].value == ")":
                if field_count < 2:
                    token = tokens[index]
                    raise DoloSyntaxError(
                        f"{_location(token)}: Herbert tuple type in new_array argument "
                        "requires at least two fields"
                    )
                return next_index + 1
            if tokens[next_index].value != ",":
                token = tokens[next_index]
                raise DoloSyntaxError(
                    f"{_location(token)}: expected ',' or ')' in Herbert tuple type"
                )
            next_index += 1

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

    def _validate_call_target(self, token: Token, *, allow_void_call: bool = False) -> None:
        if token.value in self.functions:
            return
        if token.value in HERBERT_VOID_BUILTINS:
            if allow_void_call:
                return
            raise DoloSyntaxError(
                f"{_location(token)}: built-in {token.value} has no value; "
                "use a do statement"
            )
        if token.value in HERBERT_BUILTINS:
            return
        raise DoloSyntaxError(f"{_location(token)}: unknown function call {token.value!r}")

    def _validate_call_arity(self, token: Token, expr: Expr, index: int) -> None:
        want = self.function_arities.get(token.value)
        subject = f"function {token.value}"
        if want is None and token.value in HERBERT_BUILTIN_ARITIES:
            want = HERBERT_BUILTIN_ARITIES[token.value]
            subject = f"built-in {token.value}"
        elif want is None:
            return
        got = self._constructor_arg_count(expr, index)
        if got != want:
            raise DoloSyntaxError(
                f"{_location(token)}: {subject} expects {want} {_argument_word(want)}, got {got}"
            )

    @staticmethod
    def _validate_expression_shape(expr: Expr, skipped_indexes: set[int]) -> None:
        for i, token in enumerate(expr.tokens):
            if i in skipped_indexes:
                continue
            previous = expr.tokens[i - 1] if i > 0 else None
            previous_previous = expr.tokens[i - 2] if i > 1 else None
            next_token = expr.tokens[i + 1] if i + 1 < len(expr.tokens) else None
            next_next_token = expr.tokens[i + 2] if i + 2 < len(expr.tokens) else None
            if token.value in UNSUPPORTED_EXPRESSION_PUNCTUATION:
                raise DoloSyntaxError(
                    f"{_location(token)}: unexpected {token.value!r} in expression"
                )
            if (
                previous is not None
                and _is_expression_value_end(previous)
                and _is_expression_value_start(token)
                and not (
                    previous.kind == "IDENT"
                    and token.value in {"(", "."}
                )
                and previous.value not in {"(", ",", ".", "!"}
                and previous.value not in INFIX_OPERATORS
            ):
                raise DoloSyntaxError(
                    f"{_location(token)}: expected operator before {token.value!r}"
                )
            if (
                token.value == "("
                and next_token is not None
                and next_token.value == ")"
                and (previous is None or previous.kind != "IDENT")
            ):
                raise DoloSyntaxError(
                    f"{_location(token)}: empty parenthesized expression is not implemented"
                )
            if token.value == ",":
                if previous is None or previous.value in {"(", ","}:
                    raise DoloSyntaxError(
                        f"{_location(token)}: comma requires a preceding expression"
                    )
                if next_token is None or next_token.value == ")":
                    raise DoloSyntaxError(
                        f"{_location(token)}: comma requires a following expression"
                    )
            if token.value == ".":
                if previous is None or previous.kind != "IDENT":
                    raise DoloSyntaxError(
                        f"{_location(token)}: field access requires an identifier target"
                    )
                if next_token is None or next_token.kind != "IDENT":
                    raise DoloSyntaxError(
                        f"{_location(token)}: field access requires a field name"
                    )
                if previous_previous is not None and previous_previous.value == ".":
                    raise DoloSyntaxError(
                        f"{_location(token)}: chained field access is not implemented"
                    )
                if next_next_token is not None and next_next_token.value == "(":
                    raise DoloSyntaxError(
                        f"{_location(next_next_token)}: field access is not callable"
                    )
            if token.value == "!":
                if (
                    previous is not None
                    and previous.value not in INFIX_OPERATORS
                    and previous.value not in {"(", ",", "!"}
                ):
                    raise DoloSyntaxError(
                        f"{_location(token)}: prefix '!' cannot follow an expression"
                    )
                if (
                    next_token is None
                    or next_token.value in INFIX_OPERATORS
                    or next_token.value in {")", ",", ".", "="}
                ):
                    raise DoloSyntaxError(
                        f"{_location(token)}: prefix '!' requires an operand"
                    )

    @staticmethod
    def _validate_variable_reference(token: Token, context: EmitContext) -> None:
        if token.kind != "IDENT" or token.value in context.bindings:
            return
        raise DoloSyntaxError(f"{_location(token)}: unknown variable {token.value!r}")

    @staticmethod
    def _next_value(expr: Expr, index: int, value: str) -> bool:
        return index + 1 < len(expr.tokens) and expr.tokens[index + 1].value == value

    @staticmethod
    def _validate_infix_operator(expr: Expr, index: int) -> None:
        token = expr.tokens[index]
        previous = expr.tokens[index - 1] if index > 0 else None
        next_token = expr.tokens[index + 1] if index + 1 < len(expr.tokens) else None
        if previous is None or previous.value in INFIX_OPERATORS or previous.value in {"(", ","}:
            raise DoloSyntaxError(
                f"{_location(token)}: binary operator {token.value!r} requires a left operand"
            )
        if (
            next_token is None
            or next_token.value in INFIX_OPERATORS
            or next_token.value in {")", ","}
        ):
            raise DoloSyntaxError(
                f"{_location(token)}: binary operator {token.value!r} requires a right operand"
            )


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
            out += (" " if previous == "," else "") + part
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
    return DOLO_BOOLEAN_OPERATOR_LOWERINGS.get(value, value)


def _is_expression_value_start(token: Token) -> bool:
    if token.kind in {"IDENT", "NUMBER", "STRING", "CHAR"}:
        return True
    if token.kind == "KEYWORD" and token.value in EXPRESSION_KEYWORDS:
        return True
    return token.value == "("


def _is_expression_value_end(token: Token) -> bool:
    if token.kind in {"IDENT", "NUMBER", "STRING", "CHAR"}:
        return True
    if token.kind == "KEYWORD" and token.value in EXPRESSION_KEYWORDS:
        return True
    return token.value == ")"


def _location(token: Token) -> str:
    return f"line {token.line}, column {token.column}"


def _argument_word(count: int) -> str:
    return "argument" if count == 1 else "arguments"


EXPRESSION_KEYWORDS = frozenset({"false", "true"})
INFIX_OPERATORS = frozenset(
    {"+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!=", "&&", "||"}
)
UNSUPPORTED_EXPRESSION_PUNCTUATION = frozenset({":", "{", "}"})


def emit_program(program: Program) -> str:
    return Emitter(program).emit()
