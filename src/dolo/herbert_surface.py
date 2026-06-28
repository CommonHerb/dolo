from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DOLO_BOOLEAN_OPERATOR_OWNER = "experiments/herbert/boolean_operator_candidate.herb"
DOLO_TWO_CHAR_OP_OWNER = "experiments/herbert/two_char_ops_candidate.herb"
HERBERT_BUILTIN_ARITY_OWNER = "experiments/herbert/builtin_arity_candidate.herb"
HERBERT_BUILTIN_KIND_OWNER = "experiments/herbert/builtin_kind_candidate.herb"
HERBERT_TYPE_NAME_OWNER = "experiments/herbert/type_name_candidate.herb"
RECORD_FIELD_INDEX_OWNER = "experiments/herbert/record_field_index_candidate.herb"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_VALID_BUILTIN_KINDS = frozenset({"value", "void"})


def load_dolo_boolean_operator_lowerings(root: Path | str | None = None) -> dict[str, str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / DOLO_BOOLEAN_OPERATOR_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Dolo boolean operator owner is unreadable: {DOLO_BOOLEAN_OPERATOR_OWNER}"
        ) from exc

    lowerings = _extract_boolean_operator_owner_map(owner_text)
    if not lowerings:
        raise RuntimeError(
            f"Dolo boolean operator owner declares no lowering data: {DOLO_BOOLEAN_OPERATOR_OWNER}"
        )
    return lowerings


def _extract_boolean_operator_owner_map(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Dolo boolean operator owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        value_text = return_line.removeprefix("return ").strip()
        if len(value_text) >= 2 and value_text[0] == '"' and value_text[-1] == '"':
            found[name] = value_text[1:-1]
    return dict(sorted(found.items()))


def load_dolo_two_char_ops(root: Path | str | None = None) -> frozenset[str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / DOLO_TWO_CHAR_OP_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Dolo two-char-op owner is unreadable: {DOLO_TWO_CHAR_OP_OWNER}"
        ) from exc

    markers = _extract_two_char_op_owner_map(owner_text)
    if not markers:
        raise RuntimeError(
            f"Dolo two-char-op owner declares no operator data: {DOLO_TWO_CHAR_OP_OWNER}"
        )
    invalid = {
        name: marker
        for name, marker in markers.items()
        if marker not in {0, 1}
    }
    if invalid:
        details = ", ".join(
            f"{name}={marker!r}" for name, marker in sorted(invalid.items())
        )
        raise RuntimeError(
            f"Dolo two-char-op owner has invalid marker(s): {details}"
        )
    ops = frozenset(name for name, marker in markers.items() if marker == 1)
    if not ops:
        raise RuntimeError(
            f"Dolo two-char-op owner marks no recognized operators: {DOLO_TWO_CHAR_OP_OWNER}"
        )
    return ops


def _extract_two_char_op_owner_map(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Dolo two-char-op owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        marker_text = return_line.removeprefix("return ").strip()
        if marker_text.isdigit():
            found[name] = int(marker_text)
    return dict(sorted(found.items()))


def load_herbert_builtin_arities(root: Path | str | None = None) -> dict[str, int]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / HERBERT_BUILTIN_ARITY_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert built-in arity owner is unreadable: {HERBERT_BUILTIN_ARITY_OWNER}"
        ) from exc

    arities = _extract_builtin_arity_owner_map(owner_text)
    if not arities:
        raise RuntimeError(
            f"Herbert built-in arity owner declares no arity data: {HERBERT_BUILTIN_ARITY_OWNER}"
        )
    return arities


def _extract_builtin_arity_owner_map(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Herbert built-in arity owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        arity_text = return_line.removeprefix("return ").strip()
        if arity_text.isdigit():
            found[name] = int(arity_text)
    return dict(sorted(found.items()))


def load_herbert_builtin_kinds(root: Path | str | None = None) -> dict[str, str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / HERBERT_BUILTIN_KIND_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert built-in kind owner is unreadable: {HERBERT_BUILTIN_KIND_OWNER}"
        ) from exc

    kinds = _extract_builtin_kind_owner_map(owner_text)
    if not kinds:
        raise RuntimeError(
            f"Herbert built-in kind owner declares no kind data: {HERBERT_BUILTIN_KIND_OWNER}"
        )
    invalid = {
        name: kind
        for name, kind in kinds.items()
        if kind not in _VALID_BUILTIN_KINDS
    }
    if invalid:
        details = ", ".join(
            f"{name}={kind!r}" for name, kind in sorted(invalid.items())
        )
        raise RuntimeError(
            f"Herbert built-in kind owner has invalid kind(s): {details}"
        )
    return kinds


def _extract_builtin_kind_owner_map(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Herbert built-in kind owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        value_text = return_line.removeprefix("return ").strip()
        if len(value_text) >= 2 and value_text[0] == '"' and value_text[-1] == '"':
            found[name] = value_text[1:-1]
    return dict(sorted(found.items()))


def load_herbert_type_names(root: Path | str | None = None) -> frozenset[str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / HERBERT_TYPE_NAME_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert type-name owner is unreadable: {HERBERT_TYPE_NAME_OWNER}"
        ) from exc

    markers = _extract_type_name_owner_map(owner_text)
    if not markers:
        raise RuntimeError(
            f"Herbert type-name owner declares no type-name data: {HERBERT_TYPE_NAME_OWNER}"
        )
    invalid = {
        name: marker
        for name, marker in markers.items()
        if marker not in {0, 1}
    }
    if invalid:
        details = ", ".join(
            f"{name}={marker!r}" for name, marker in sorted(invalid.items())
        )
        raise RuntimeError(
            f"Herbert type-name owner has invalid marker(s): {details}"
        )
    names = frozenset(name for name, marker in markers.items() if marker == 1)
    if not names:
        raise RuntimeError(
            f"Herbert type-name owner marks no recognized type names: {HERBERT_TYPE_NAME_OWNER}"
        )
    return names


def _extract_type_name_owner_map(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Herbert type-name owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        marker_text = return_line.removeprefix("return ").strip()
        if marker_text.isdigit():
            found[name] = int(marker_text)
    return dict(sorted(found.items()))


@dataclass(frozen=True)
class _HerbertToken:
    kind: str
    value: object
    line: int
    column: int


@dataclass(frozen=True)
class _HerbertFunction:
    name: str
    params: tuple[str, ...]
    body: tuple[object, ...]


@dataclass(frozen=True)
class _HerbertReturnStmt:
    expr: object


@dataclass(frozen=True)
class _HerbertIfStmt:
    condition: object
    then_body: tuple[object, ...]
    else_body: tuple[object, ...]


@dataclass(frozen=True)
class _HerbertIntExpr:
    value: int


@dataclass(frozen=True)
class _HerbertStringExpr:
    value: str


@dataclass(frozen=True)
class _HerbertVarExpr:
    name: str


@dataclass(frozen=True)
class _HerbertCallExpr:
    name: str
    args: tuple[object, ...]


@dataclass(frozen=True)
class _HerbertTupleExpr:
    items: tuple[object, ...]


class _HerbertReturn(Exception):
    def __init__(self, value: object):
        self.value = value


class _HerbertSubsetProgram:
    def __init__(self, functions: dict[str, _HerbertFunction]):
        self._functions = functions

    def has_function(self, name: str) -> bool:
        return name in self._functions

    def call(self, name: str, args: tuple[object, ...]) -> object:
        return self._call(name, args, depth=0)

    def _call(self, name: str, args: tuple[object, ...], *, depth: int) -> object:
        if depth > 10000:
            raise RuntimeError(f"Herbert owner recursion limit exceeded in {name}")
        builtin = _HERBERT_SUBSET_BUILTINS.get(name)
        if builtin is not None:
            return builtin(args)
        function = self._functions.get(name)
        if function is None:
            raise RuntimeError(f"Herbert owner calls unknown function {name!r}")
        if len(args) != len(function.params):
            raise RuntimeError(
                f"Herbert owner function {name} expects {len(function.params)} "
                f"arguments, got {len(args)}"
            )
        env = dict(zip(function.params, args))
        try:
            self._eval_statements(function.body, env, depth=depth)
        except _HerbertReturn as result:
            return result.value
        raise RuntimeError(f"Herbert owner function {name} returned no value")

    def _eval_statements(
        self,
        statements: tuple[object, ...],
        env: dict[str, object],
        *,
        depth: int,
    ) -> None:
        for statement in statements:
            if isinstance(statement, _HerbertReturnStmt):
                raise _HerbertReturn(self._eval_expr(statement.expr, env, depth=depth))
            if isinstance(statement, _HerbertIfStmt):
                branch = (
                    statement.then_body
                    if self._truthy(self._eval_expr(statement.condition, env, depth=depth))
                    else statement.else_body
                )
                self._eval_statements(branch, env, depth=depth)
                continue
            raise RuntimeError(f"Herbert owner has unknown statement {statement!r}")

    def _eval_expr(
        self,
        expr: object,
        env: dict[str, object],
        *,
        depth: int,
    ) -> object:
        if isinstance(expr, _HerbertIntExpr):
            return expr.value
        if isinstance(expr, _HerbertStringExpr):
            return expr.value
        if isinstance(expr, _HerbertTupleExpr):
            return tuple(self._eval_expr(item, env, depth=depth) for item in expr.items)
        if isinstance(expr, _HerbertVarExpr):
            if expr.name not in env:
                raise RuntimeError(f"Herbert owner reads unknown variable {expr.name!r}")
            return env[expr.name]
        if isinstance(expr, _HerbertCallExpr):
            args = tuple(self._eval_expr(arg, env, depth=depth) for arg in expr.args)
            return self._call(expr.name, args, depth=depth + 1)
        raise RuntimeError(f"Herbert owner has unknown expression {expr!r}")

    @staticmethod
    def _truthy(value: object) -> bool:
        return bool(value)


def _builtin_equal(args: tuple[object, ...]) -> bool:
    _require_herbert_builtin_arity("equal", args, 2)
    return args[0] == args[1]


def _builtin_empty(args: tuple[object, ...]) -> bool:
    _require_herbert_builtin_arity("empty", args, 1)
    return len(_require_herbert_sequence("empty", args[0])) == 0


def _builtin_first(args: tuple[object, ...]) -> object:
    _require_herbert_builtin_arity("first", args, 1)
    value = _require_herbert_sequence("first", args[0])
    if not value:
        raise RuntimeError("Herbert owner called first on an empty sequence")
    return value[0]


def _builtin_rest(args: tuple[object, ...]) -> tuple[object, ...]:
    _require_herbert_builtin_arity("rest", args, 1)
    value = _require_herbert_sequence("rest", args[0])
    return tuple(value[1:])


def _builtin_plus(args: tuple[object, ...]) -> int:
    _require_herbert_builtin_arity("plus", args, 2)
    left, right = args
    if type(left) is not int or type(right) is not int:
        raise RuntimeError("Herbert owner plus expects integer arguments")
    return left + right


def _require_herbert_builtin_arity(
    name: str,
    args: tuple[object, ...],
    want: int,
) -> None:
    if len(args) != want:
        raise RuntimeError(
            f"Herbert owner built-in {name} expects {want} arguments, got {len(args)}"
        )


def _require_herbert_sequence(name: str, value: object) -> tuple[object, ...] | str:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, str):
        return value
    raise RuntimeError(f"Herbert owner built-in {name} expects a sequence")


_HERBERT_SUBSET_BUILTINS = {
    "equal": _builtin_equal,
    "empty": _builtin_empty,
    "first": _builtin_first,
    "rest": _builtin_rest,
    "plus": _builtin_plus,
}


class _HerbertSubsetParser:
    def __init__(self, tokens: tuple[_HerbertToken, ...]):
        self._tokens = tokens
        self._index = 0

    def parse_program(self) -> _HerbertSubsetProgram:
        functions: dict[str, _HerbertFunction] = {}
        while not self._at_kind("EOF"):
            function = self._parse_function()
            if function.name in functions:
                self._fail_current(
                    f"Herbert owner repeats function {function.name!r}"
                )
            functions[function.name] = function
        return _HerbertSubsetProgram(functions)

    def _parse_function(self) -> _HerbertFunction:
        self._expect_value("func")
        name = self._expect_ident()
        self._expect_value("(")
        params: list[str] = []
        if not self._match_value(")"):
            while True:
                params.append(self._expect_ident())
                if self._match_value(")"):
                    break
                self._expect_value(",")
        self._expect_value(":")
        body = self._parse_block(stop_values=frozenset({"end"}))
        self._expect_value("end")
        return _HerbertFunction(name=name, params=tuple(params), body=tuple(body))

    def _parse_block(self, *, stop_values: frozenset[str]) -> list[object]:
        statements: list[object] = []
        while not self._at_kind("EOF") and not self._at_any(stop_values):
            statements.append(self._parse_statement())
        return statements

    def _parse_statement(self) -> object:
        if self._match_value("return"):
            return _HerbertReturnStmt(self._parse_expression())
        if self._match_value("if"):
            condition = self._parse_expression()
            self._expect_value(":")
            then_body = self._parse_block(stop_values=frozenset({"else", "end"}))
            else_body: tuple[object, ...] = ()
            if self._match_value("else"):
                self._expect_value(":")
                else_body = tuple(self._parse_block(stop_values=frozenset({"end"})))
            self._expect_value("end")
            return _HerbertIfStmt(
                condition=condition,
                then_body=tuple(then_body),
                else_body=else_body,
            )
        self._fail_current("Herbert owner expected return or if statement")

    def _parse_expression(self) -> object:
        return self._parse_primary()

    def _parse_primary(self) -> object:
        token = self._peek()
        if token.kind == "INT":
            self._advance()
            return _HerbertIntExpr(token.value)
        if token.kind == "STRING":
            self._advance()
            return _HerbertStringExpr(token.value)
        if token.kind == "IDENT":
            name = str(token.value)
            self._advance()
            if self._match_value("("):
                args: list[object] = []
                if not self._match_value(")"):
                    while True:
                        args.append(self._parse_expression())
                        if self._match_value(")"):
                            break
                        self._expect_value(",")
                return _HerbertCallExpr(name=name, args=tuple(args))
            return _HerbertVarExpr(name=name)
        if self._match_value("("):
            if self._match_value(")"):
                return _HerbertTupleExpr(())
            first = self._parse_expression()
            if not self._match_value(","):
                self._expect_value(")")
                return first
            items = [first]
            if self._match_value(")"):
                return _HerbertTupleExpr(tuple(items))
            while True:
                items.append(self._parse_expression())
                if self._match_value(")"):
                    break
                self._expect_value(",")
            return _HerbertTupleExpr(tuple(items))
        self._fail_current("Herbert owner expected expression")

    def _peek(self) -> _HerbertToken:
        return self._tokens[self._index]

    def _advance(self) -> _HerbertToken:
        token = self._peek()
        self._index += 1
        return token

    def _match_value(self, value: str) -> bool:
        if self._peek().value != value:
            return False
        self._advance()
        return True

    def _expect_value(self, value: str) -> None:
        if not self._match_value(value):
            self._fail_current(f"Herbert owner expected {value!r}")

    def _expect_ident(self) -> str:
        token = self._peek()
        if token.kind != "IDENT":
            self._fail_current("Herbert owner expected identifier")
        self._advance()
        return str(token.value)

    def _at_kind(self, kind: str) -> bool:
        return self._peek().kind == kind

    def _at_any(self, values: frozenset[str]) -> bool:
        return self._peek().value in values

    def _fail_current(self, message: str) -> None:
        token = self._peek()
        raise RuntimeError(
            f"{message} at line {token.line}, column {token.column}"
        )


def load_record_field_index_owner(
    root: Path | str | None = None,
) -> _HerbertSubsetProgram:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / RECORD_FIELD_INDEX_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert record-field-index owner is unreadable: {RECORD_FIELD_INDEX_OWNER}"
        ) from exc

    program = _parse_herbert_subset(owner_text)
    if not program.has_function("field_index"):
        raise RuntimeError(
            f"Herbert record-field-index owner declares no field_index: "
            f"{RECORD_FIELD_INDEX_OWNER}"
        )
    return program


def _parse_herbert_subset(text: str) -> _HerbertSubsetProgram:
    return _HerbertSubsetParser(_tokenize_herbert_subset(text)).parse_program()


def _tokenize_herbert_subset(text: str) -> tuple[_HerbertToken, ...]:
    tokens: list[_HerbertToken] = []
    index = 0
    line = 1
    column = 1
    while index < len(text):
        ch = text[index]
        if ch in " \t\r":
            index += 1
            column += 1
            continue
        if ch == "\n":
            index += 1
            line += 1
            column = 1
            continue
        if ch == "#":
            while index < len(text) and text[index] != "\n":
                index += 1
                column += 1
            continue
        if ch.isalpha() or ch == "_":
            start = index
            start_column = column
            while index < len(text) and (
                text[index].isalnum() or text[index] == "_"
            ):
                index += 1
                column += 1
            tokens.append(
                _HerbertToken("IDENT", text[start:index], line, start_column)
            )
            continue
        if ch.isdigit():
            start = index
            start_column = column
            while index < len(text) and text[index].isdigit():
                index += 1
                column += 1
            tokens.append(
                _HerbertToken("INT", int(text[start:index]), line, start_column)
            )
            continue
        if ch == '"':
            start_line = line
            start_column = column
            index += 1
            column += 1
            chars: list[str] = []
            while index < len(text):
                current = text[index]
                if current == '"':
                    index += 1
                    column += 1
                    tokens.append(
                        _HerbertToken(
                            "STRING",
                            "".join(chars),
                            start_line,
                            start_column,
                        )
                    )
                    break
                if current == "\\":
                    if index + 1 >= len(text):
                        raise RuntimeError(
                            "Herbert owner has unterminated escape at "
                            f"line {line}, column {column}"
                        )
                    escaped = text[index + 1]
                    chars.append(_HERBERT_STRING_ESCAPES.get(escaped, escaped))
                    index += 2
                    column += 2
                    continue
                if current == "\n":
                    raise RuntimeError(
                        "Herbert owner has unterminated string at "
                        f"line {start_line}, column {start_column}"
                    )
                chars.append(current)
                index += 1
                column += 1
            else:
                raise RuntimeError(
                    "Herbert owner has unterminated string at "
                    f"line {start_line}, column {start_column}"
                )
            continue
        if ch in "(),:":
            tokens.append(_HerbertToken("PUNCT", ch, line, column))
            index += 1
            column += 1
            continue
        raise RuntimeError(
            f"Herbert owner has unexpected character {ch!r} "
            f"at line {line}, column {column}"
        )
    tokens.append(_HerbertToken("EOF", "", line, column))
    return tuple(tokens)


_HERBERT_STRING_ESCAPES = {
    "n": "\n",
    "r": "\r",
    "t": "\t",
    '"': '"',
    "\\": "\\",
}


_DOLO_BOOLEAN_OPERATOR_LOWERINGS_BY_OWNER = load_dolo_boolean_operator_lowerings()
_DOLO_TWO_CHAR_OPS_BY_OWNER = load_dolo_two_char_ops()
_HERBERT_BUILTIN_ARITIES_BY_OWNER = load_herbert_builtin_arities()
_HERBERT_BUILTIN_KINDS_BY_OWNER = load_herbert_builtin_kinds()
_HERBERT_TYPE_NAMES_BY_OWNER = load_herbert_type_names()
_RECORD_FIELD_INDEX_BY_OWNER = load_record_field_index_owner()
DOLO_BOOLEAN_OPERATOR_LOWERINGS = dict(_DOLO_BOOLEAN_OPERATOR_LOWERINGS_BY_OWNER)
HERBERT_BUILTIN_ARITIES = dict(_HERBERT_BUILTIN_ARITIES_BY_OWNER)
HERBERT_BUILTIN_KINDS = dict(_HERBERT_BUILTIN_KINDS_BY_OWNER)
HERBERT_VALUE_BUILTINS = frozenset(
    name for name, kind in _HERBERT_BUILTIN_KINDS_BY_OWNER.items() if kind == "value"
)
HERBERT_VOID_BUILTINS = frozenset(
    name for name, kind in _HERBERT_BUILTIN_KINDS_BY_OWNER.items() if kind == "void"
)
HERBERT_BUILTINS = frozenset(_HERBERT_BUILTIN_KINDS_BY_OWNER)
HERBERT_TYPE_NAMES = frozenset(_HERBERT_TYPE_NAMES_BY_OWNER)


def dolo_boolean_operator_lowering(name: str) -> str | None:
    return _DOLO_BOOLEAN_OPERATOR_LOWERINGS_BY_OWNER.get(name)


def is_dolo_two_char_op(name: str) -> bool:
    return name in _DOLO_TWO_CHAR_OPS_BY_OWNER


def herbert_builtin_arity(name: str) -> int | None:
    return _HERBERT_BUILTIN_ARITIES_BY_OWNER.get(name)


def herbert_builtin_kind(name: str) -> str | None:
    return _HERBERT_BUILTIN_KINDS_BY_OWNER.get(name)


def is_herbert_type_name(name: str) -> bool:
    return name in _HERBERT_TYPE_NAMES_BY_OWNER


def record_field_index(fields: tuple[str, ...], name: str) -> int | None:
    value = _RECORD_FIELD_INDEX_BY_OWNER.call("field_index", (tuple(fields), name))
    if type(value) is int:
        return value
    return None


DOLO_CLOSING_DELIMITER_OWNER = "experiments/herbert/closing_delimiters_candidate.herb"
def load_dolo_closing_delimiters(root: Path | str | None = None) -> dict[str, str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / DOLO_CLOSING_DELIMITER_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Dolo closing-delimiter owner is unreadable: {DOLO_CLOSING_DELIMITER_OWNER}"
        ) from exc

    delimiters = _extract_closing_delimiter_owner_map(owner_text)
    if not delimiters:
        raise RuntimeError(
            f"Dolo closing-delimiter owner declares no delimiter data: {DOLO_CLOSING_DELIMITER_OWNER}"
        )
    return delimiters


def _extract_closing_delimiter_owner_map(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Dolo closing-delimiter owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        value_text = return_line.removeprefix("return ").strip()
        if len(value_text) >= 2 and value_text[0] == '"' and value_text[-1] == '"':
            found[name] = value_text[1:-1]
    return dict(sorted(found.items()))


_DOLO_CLOSING_DELIMITERS_BY_OWNER = load_dolo_closing_delimiters()
def dolo_opening_delimiter_for(name: str) -> str | None:
    return _DOLO_CLOSING_DELIMITERS_BY_OWNER.get(name)




DOLO_INFIX_OPERATOR_OWNER = "experiments/herbert/infix_operators_candidate.herb"
def load_dolo_infix_operators(root: Path | str | None = None) -> frozenset[str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / DOLO_INFIX_OPERATOR_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Dolo infix-operator owner is unreadable: {DOLO_INFIX_OPERATOR_OWNER}"
        ) from exc

    markers = _extract_infix_operator_owner_map(owner_text)
    if not markers:
        raise RuntimeError(
            f"Dolo infix-operator owner declares no operator data: {DOLO_INFIX_OPERATOR_OWNER}"
        )
    invalid = {
        name: marker
        for name, marker in markers.items()
        if marker not in {0, 1}
    }
    if invalid:
        details = ", ".join(
            f"{name}={marker!r}" for name, marker in sorted(invalid.items())
        )
        raise RuntimeError(
            f"Dolo infix-operator owner has invalid marker(s): {details}"
        )
    ops = frozenset(name for name, marker in markers.items() if marker == 1)
    if not ops:
        raise RuntimeError(
            f"Dolo infix-operator owner marks no recognized operators: {DOLO_INFIX_OPERATOR_OWNER}"
        )
    return ops


def _extract_infix_operator_owner_map(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    seen_lookup_names: set[str] = set()
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        if name in seen_lookup_names:
            raise RuntimeError(
                f"Dolo infix-operator owner repeats lookup name {name!r}"
            )
        seen_lookup_names.add(name)
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        marker_text = return_line.removeprefix("return ").strip()
        if marker_text.isdigit():
            found[name] = int(marker_text)
    return dict(sorted(found.items()))


_DOLO_INFIX_OPERATORS_BY_OWNER = load_dolo_infix_operators()
def is_dolo_infix_operator(name: str) -> bool:
    return name in _DOLO_INFIX_OPERATORS_BY_OWNER

