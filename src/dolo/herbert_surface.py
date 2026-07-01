from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


DOLO_BOOLEAN_OPERATOR_OWNER = "experiments/herbert/boolean_operator_candidate.herb"
DOLO_TWO_CHAR_OP_OWNER = "experiments/herbert/two_char_ops_candidate.herb"
HERBERT_BUILTIN_ARITY_OWNER = "experiments/herbert/builtin_arity_candidate.herb"
HERBERT_BUILTIN_KIND_OWNER = "experiments/herbert/builtin_kind_candidate.herb"
HERBERT_TYPE_NAME_OWNER = "experiments/herbert/type_name_candidate.herb"
RECORD_FIELD_INDEX_OWNER = "experiments/herbert/record_field_index_candidate.herb"
ARRAY_MUTATION_SHAPE_OWNER = "experiments/herbert/array_mutation_shape_candidate.herb"
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

    lowerings = _seed_string_value_map(
        repo_root, owner_text, "boolean_operator", "Dolo boolean operator owner"
    )
    if not lowerings:
        raise RuntimeError(
            f"Dolo boolean operator owner declares no lowering data: {DOLO_BOOLEAN_OPERATOR_OWNER}"
        )
    return lowerings


def load_dolo_two_char_ops(root: Path | str | None = None) -> frozenset[str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / DOLO_TWO_CHAR_OP_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Dolo two-char-op owner is unreadable: {DOLO_TWO_CHAR_OP_OWNER}"
        ) from exc

    ops = _seed_marker_set(
        repo_root, owner_text, "two_char_op", "Dolo two-char-op owner"
    )
    if not ops:
        raise RuntimeError(
            f"Dolo two-char-op owner marks no recognized operators: {DOLO_TWO_CHAR_OP_OWNER}"
        )
    return ops


def load_herbert_builtin_arities(root: Path | str | None = None) -> dict[str, int]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / HERBERT_BUILTIN_ARITY_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert built-in arity owner is unreadable: {HERBERT_BUILTIN_ARITY_OWNER}"
        ) from exc

    arities = _seed_int_value_map(
        repo_root, owner_text, "builtin_arity", "Herbert built-in arity owner"
    )
    if not arities:
        raise RuntimeError(
            f"Herbert built-in arity owner declares no arity data: {HERBERT_BUILTIN_ARITY_OWNER}"
        )
    return arities


def load_herbert_builtin_kinds(root: Path | str | None = None) -> dict[str, str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / HERBERT_BUILTIN_KIND_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert built-in kind owner is unreadable: {HERBERT_BUILTIN_KIND_OWNER}"
        ) from exc

    kinds = _seed_string_value_map(
        repo_root,
        owner_text,
        "builtin_kind",
        "Herbert built-in kind owner",
        allowed=_VALID_BUILTIN_KINDS,
    )
    if not kinds:
        raise RuntimeError(
            f"Herbert built-in kind owner declares no kind data: {HERBERT_BUILTIN_KIND_OWNER}"
        )
    return kinds


def load_herbert_type_names(root: Path | str | None = None) -> frozenset[str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / HERBERT_TYPE_NAME_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert type-name owner is unreadable: {HERBERT_TYPE_NAME_OWNER}"
        ) from exc

    names = _seed_marker_set(
        repo_root, owner_text, "type_name", "Herbert type-name owner"
    )
    if not names:
        raise RuntimeError(
            f"Herbert type-name owner marks no recognized type names: {HERBERT_TYPE_NAME_OWNER}"
        )
    return names


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
class _HerbertLetStmt:
    name: str
    expr: object


@dataclass(frozen=True)
class _HerbertDoStmt:
    expr: object


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
class _HerbertBinaryExpr:
    operator: str
    left: object
    right: object


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
            if isinstance(statement, _HerbertLetStmt):
                env[statement.name] = self._eval_expr(statement.expr, env, depth=depth)
                continue
            if isinstance(statement, _HerbertDoStmt):
                self._eval_expr(statement.expr, env, depth=depth)
                continue
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
            if expr.name in env:
                return env[expr.name]
            if expr.name in _HERBERT_TYPE_NAMES:
                return expr.name
            raise RuntimeError(f"Herbert owner reads unknown variable {expr.name!r}")
        if isinstance(expr, _HerbertCallExpr):
            args = tuple(self._eval_expr(arg, env, depth=depth) for arg in expr.args)
            return self._call(expr.name, args, depth=depth + 1)
        if isinstance(expr, _HerbertBinaryExpr):
            left = self._eval_expr(expr.left, env, depth=depth)
            right = self._eval_expr(expr.right, env, depth=depth)
            if expr.operator == "==":
                return left == right
            if expr.operator == "+":
                return _herbert_int_add(left, right)
            if expr.operator == "-":
                return _herbert_int_subtract(left, right)
            raise RuntimeError(
                f"Herbert owner has unsupported binary operator {expr.operator!r}"
            )
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
    return _herbert_int_add(args[0], args[1])


def _builtin_count(args: tuple[object, ...]) -> int:
    _require_herbert_builtin_arity("count", args, 1)
    return len(_require_herbert_sequence("count", args[0]))


def _builtin_get(args: tuple[object, ...]) -> object:
    _require_herbert_builtin_arity("get", args, 2)
    value = _require_herbert_sequence("get", args[0])
    index = args[1]
    if type(index) is not int:
        raise RuntimeError("Herbert owner get expects an integer index")
    if index < 0 or index >= len(value):
        raise RuntimeError("Herbert owner get index is out of bounds")
    return value[index]


def _builtin_new_array(args: tuple[object, ...]) -> list[object]:
    _require_herbert_builtin_arity("new_array", args, 1)
    return []


def _builtin_add(args: tuple[object, ...]) -> None:
    _require_herbert_builtin_arity("add", args, 2)
    if not isinstance(args[0], list):
        raise RuntimeError("Herbert owner add expects an array")
    args[0].append(args[1])
    return None


def _builtin_array_type(args: tuple[object, ...]) -> tuple[str, object]:
    _require_herbert_builtin_arity("array", args, 1)
    return ("array", args[0])


def _herbert_int_add(left: object, right: object) -> int:
    if type(left) is not int or type(right) is not int:
        raise RuntimeError("Herbert owner + expects integer arguments")
    return left + right


def _herbert_int_subtract(left: object, right: object) -> int:
    if type(left) is not int or type(right) is not int:
        raise RuntimeError("Herbert owner - expects integer arguments")
    return left - right


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
    "add": _builtin_add,
    "array": _builtin_array_type,
    "count": _builtin_count,
    "equal": _builtin_equal,
    "empty": _builtin_empty,
    "first": _builtin_first,
    "get": _builtin_get,
    "new_array": _builtin_new_array,
    "rest": _builtin_rest,
    "plus": _builtin_plus,
}

_HERBERT_TYPE_NAMES = frozenset({"bool", "buffer", "int", "string"})


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
        if self._match_value("let"):
            name = self._expect_ident()
            self._expect_value("=")
            return _HerbertLetStmt(name=name, expr=self._parse_expression())
        if self._match_value("do"):
            return _HerbertDoStmt(self._parse_expression())
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
        self._fail_current("Herbert owner expected return, let, do, or if statement")

    def _parse_expression(self) -> object:
        return self._parse_equality()

    def _parse_equality(self) -> object:
        expr = self._parse_addition()
        while self._match_value("=="):
            expr = _HerbertBinaryExpr(
                operator="==",
                left=expr,
                right=self._parse_addition(),
            )
        return expr

    def _parse_addition(self) -> object:
        expr = self._parse_primary()
        while self._peek().value in {"+", "-"}:
            operator = str(self._advance().value)
            expr = _HerbertBinaryExpr(
                operator=operator,
                left=expr,
                right=self._parse_primary(),
            )
        return expr

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


def load_array_mutation_shape(
    root: Path | str | None = None,
) -> tuple[frozenset[str], int, str]:
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / ARRAY_MUTATION_SHAPE_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert array-mutation shape owner is unreadable: {ARRAY_MUTATION_SHAPE_OWNER}"
        ) from exc

    required = (
        "do_admits_kind",
        "do_statement_call_count",
        "do_statement_keyword",
    )
    missing = [
        name
        for name in required
        if not _herbert_text_declares_function(owner_text, name)
    ]
    if missing:
        raise RuntimeError(
            "Herbert array-mutation shape owner is missing required function(s): "
            + ", ".join(missing)
        )

    stdout = _run_owner_program_on_seed(
        repo_root, owner_text, "Herbert array-mutation shape owner"
    )
    return _parse_array_mutation_shape_stdout(stdout)


def _herbert_text_declares_function(text: str, name: str) -> bool:
    pattern = rf"(?m)^\s*func\s+{re.escape(name)}\s*\("
    return re.search(pattern, text) is not None


def _run_owner_program_on_seed(
    repo_root: Path, program_text: str, label: str
) -> str:
    """Compile+run a Herbert program through the verified pinned seed; return its stdout.

    Fail-closed: a missing/garbage seed, a compile failure, a non-ELF a.out, a non-zero
    run, or any stderr raises RuntimeError. There is NO Python fallback -- the seed is the
    executor. `label` is woven into the error messages for the calling authority.
    """
    seed_path = _resolve_verified_herbert_seed(repo_root)
    try:
        with tempfile.TemporaryDirectory(
            prefix="dolo-owner-seed-",
            dir="/tmp",
        ) as tmp_name:
            tmp = Path(tmp_name)
            compiler = tmp / "herbert-gen1"
            shutil.copy2(seed_path, compiler)
            compiler.chmod(compiler.stat().st_mode | 0o111)

            run_dir = tmp / "owner.run"
            run_dir.mkdir()
            compile_result = subprocess.run(
                [str(compiler)],
                input=program_text,
                cwd=run_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if compile_result.returncode != 0:
                raise RuntimeError(
                    f"{label} failed during seed compile: "
                    f"{_subprocess_summary(compile_result)}"
                )

            executable = run_dir / "a.out"
            if not executable.is_file():
                raise RuntimeError(
                    f"{label} seed compile produced no "
                    f"a.out: {_subprocess_summary(compile_result)}"
                )
            try:
                magic = executable.read_bytes()[:4]
            except OSError as exc:
                raise RuntimeError(
                    f"{label} produced unreadable a.out"
                ) from exc
            if magic != b"\x7fELF":
                raise RuntimeError(
                    f"{label} seed compile produced "
                    f"non-ELF a.out (magic={magic.hex()})"
                )
            executable.chmod(executable.stat().st_mode | 0o111)

            run_result = subprocess.run(
                [str(executable)],
                cwd=run_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if run_result.returncode != 0:
                raise RuntimeError(
                    f"{label} executable failed: "
                    f"{_subprocess_summary(run_result)}"
                )
            if run_result.stderr:
                raise RuntimeError(
                    f"{label} executable wrote stderr: "
                    f"{_first_line(run_result.stderr)!r}"
                )
            return run_result.stdout
    except RuntimeError:
        raise
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        raise RuntimeError(
            f"{label} failed during seed execution"
        ) from exc


# <=7 strings render to 14 words and <=7 ints to 7 words -- both under the seed's 15-word
# main()-return cap (native_compile_fragment nc_type_is_renderable_aggregate). A key the owner
# does not declare is the sentinel-probe key; it must not collide with a real domain key.
_SEED_VALUE_CHUNK = 7
_SEED_ABSENT_KEY = "__dolo_absent_domain_key__"


def _herb_string_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _seed_owner_prefix(owner_text: str, label: str) -> str:
    """The owner source up to (not including) its own `func main()` -- the lookup if-chain plus
    `key_list` plus any helpers. The boundary appends its own query main() to this prefix.
    Line-anchored on the `func main(` declaration so a comment/string mentioning it cannot truncate
    the prefix."""
    match = re.search(r"(?m)^\s*func\s+main\s*\(", owner_text)
    if match is None:
        raise RuntimeError(f"{label} declares no func main()")
    return owner_text[: match.start()]


def _seed_eval_main(repo_root: Path, prefix: str, return_expr: str, label: str) -> object:
    program = prefix + f"func main():\n    return {return_expr}\nend\n"
    stdout = _run_owner_program_on_seed(repo_root, program, label)
    try:
        return ast.literal_eval(stdout.strip())
    except (SyntaxError, ValueError) as exc:
        raise RuntimeError(
            f"{label} emitted unparsable stdout: {stdout!r}"
        ) from exc


def _seed_owner_table(
    repo_root: Path, owner_text: str, lookup_fn: str, label: str
) -> dict[str, object]:
    """Materialize {key: value} for a lookup-table owner BY EXECUTING IT ON THE PINNED SEED.

    KEYS come from the seed running the owner's `key_list()` (the owner's declared domain);
    VALUES come from the seed running the owner's `lookup_fn(key)` if-chain. Python only splits
    the CSV and ast.literal_eval's the rendered tuple -- no table decision is Python-computed.
    Returns the RAW {key: value} for every declared key (no dropping); the shape helpers
    (int/string value-map, marker-set) apply the fail-closed domain + value validation.
    Fail-closed throughout (any seed/parse error raises; no Python fallback)."""
    for required in (lookup_fn, "key_list"):
        if not _herbert_text_declares_function(owner_text, required):
            raise RuntimeError(f"{label} declares no {required}")
    prefix = _seed_owner_prefix(owner_text, label)

    # KEYS -- the owner's declared domain, returned by the seed as a single CSV string.
    csv = _seed_eval_main(repo_root, prefix, "key_list()", label)
    if not isinstance(csv, str) or not csv:
        raise RuntimeError(
            f"{label} key_list did not return a non-empty string: {csv!r}"
        )
    keys = csv.split(",")
    for key in keys:
        if not key:
            raise RuntimeError(f"{label} key_list has an empty key: {csv!r}")
        if key != key.strip():
            raise RuntimeError(
                f"{label} key_list key {key!r} has surrounding whitespace: {csv!r}"
            )
    if len(set(keys)) != len(keys):
        raise RuntimeError(f"{label} key_list repeats a key: {csv!r}")

    # VALUES -- computed by the owner's lookup if-chain, executed by the seed, batched under the
    # seed's 15-word render cap.
    values: list[object] = []
    for start in range(0, len(keys), _SEED_VALUE_CHUNK):
        group = keys[start : start + _SEED_VALUE_CHUNK]
        calls = ", ".join(
            f"{lookup_fn}({_herb_string_literal(key)})" for key in group
        )
        expr = calls if len(group) == 1 else f"({calls})"
        result = _seed_eval_main(repo_root, prefix, expr, label)
        if len(group) == 1:
            values.append(result)
        elif isinstance(result, tuple) and len(result) == len(group):
            values.extend(result)
        else:
            raise RuntimeError(
                f"{label} value batch returned an unexpected shape: {result!r}"
            )

    return dict(zip(keys, values))


def _seed_owner_out_of_domain_value(
    repo_root: Path, owner_text: str, lookup_fn: str, label: str
) -> object:
    """What the owner returns for a key OUTSIDE its domain -- learned by asking the owner (a
    guaranteed-absent probe key), never assumed by Python. A value-map key whose lookup returns
    this is a key_list/if-chain drift (or an entry that fell through to the default) and MUST fail
    closed -- matching the deleted scraper, which surfaced such an entry for value validation."""
    prefix = _seed_owner_prefix(owner_text, label)
    return _seed_eval_main(
        repo_root, prefix, f"{lookup_fn}({_herb_string_literal(_SEED_ABSENT_KEY)})", label
    )


def _reject_out_of_domain(table: dict[str, object], sentinel: object, label: str) -> None:
    drifted = sorted(name for name, value in table.items() if value == sentinel)
    if drifted:
        raise RuntimeError(
            f"{label} declares {', '.join(drifted)} in key_list but the lookup returns the "
            f"out-of-domain value {sentinel!r} for them -- key_list drifted from the if-chain"
        )


def _seed_int_value_map(
    repo_root: Path, owner_text: str, lookup_fn: str, label: str
) -> dict[str, int]:
    """value-map: every declared key maps to its if-chain int. A key whose lookup returns the
    out-of-domain value fails closed (drift), never silently vanishes."""
    table = _seed_owner_table(repo_root, owner_text, lookup_fn, label)
    sentinel = _seed_owner_out_of_domain_value(repo_root, owner_text, lookup_fn, label)
    _reject_out_of_domain(table, sentinel, label)
    result: dict[str, int] = {}
    for name, value in table.items():
        if type(value) is not int:
            raise RuntimeError(f"{label} returned a non-integer value for {name!r}: {value!r}")
        result[name] = value
    return dict(sorted(result.items()))


def _seed_string_value_map(
    repo_root: Path,
    owner_text: str,
    lookup_fn: str,
    label: str,
    *,
    allowed: frozenset[str] | None = None,
) -> dict[str, str]:
    """value-map: every declared key maps to a non-empty if-chain string (empty would be shadowed
    by the emitter's `lowering or value` fallback). Out-of-domain / invalid values fail closed."""
    table = _seed_owner_table(repo_root, owner_text, lookup_fn, label)
    sentinel = _seed_owner_out_of_domain_value(repo_root, owner_text, lookup_fn, label)
    _reject_out_of_domain(table, sentinel, label)
    result: dict[str, str] = {}
    invalid: dict[str, object] = {}
    for name, value in table.items():
        if type(value) is not str or not value:
            raise RuntimeError(
                f"{label} returned a non-string/empty value for {name!r}: {value!r}"
            )
        if allowed is not None and value not in allowed:
            invalid[name] = value
            continue
        result[name] = value
    if invalid:
        details = ", ".join(f"{n}={v!r}" for n, v in sorted(invalid.items()))
        raise RuntimeError(f"{label} has invalid value(s): {details}")
    return dict(sorted(result.items()))


def _seed_marker_set(
    repo_root: Path, owner_text: str, lookup_fn: str, label: str
) -> frozenset[str]:
    """marker-set: each declared key carries a 0/1 marker; membership is the marker==1 set. A key
    whose marker is 0 (a non-member, or a member perturbed off) is simply not in the set -- exactly
    the deleted scraper's marker==1 filter."""
    table = _seed_owner_table(repo_root, owner_text, lookup_fn, label)
    invalid = {
        name: value
        for name, value in table.items()
        if type(value) is not int or value not in {0, 1}
    }
    if invalid:
        details = ", ".join(f"{n}={v!r}" for n, v in sorted(invalid.items()))
        raise RuntimeError(f"{label} has invalid marker(s): {details}")
    return frozenset(name for name, value in table.items() if value == 1)


def _resolve_verified_herbert_seed(repo_root: Path) -> Path:
    env_seed = os.environ.get("DOLO_HERBERT_SEED")
    if env_seed:
        seed_path = Path(env_seed).expanduser()
    else:
        seed_path = (
            repo_root
            / ".."
            / "herbert-pin"
            / "bootstrap"
            / "seed"
            / "gen1.seed"
        )
    seed_path = seed_path.resolve()
    expected = _herbert_lock_value(repo_root, "HERBERT_SEED_SHA256")
    try:
        actual = _sha256_file(seed_path)
    except OSError as exc:
        raise RuntimeError(f"Herbert seed is missing or unreadable: {seed_path}") from exc
    if actual != expected:
        raise RuntimeError(
            f"Herbert seed sha256 {actual} does not match pin {expected}: {seed_path}"
        )
    return seed_path


def _herbert_lock_value(repo_root: Path, key: str) -> str:
    lock_path = repo_root / "HERBERT.lock"
    try:
        lines = lock_path.read_text().splitlines()
    except OSError as exc:
        raise RuntimeError("Dolo Herbert lock is unreadable: HERBERT.lock") from exc
    prefix = key + "="
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip().strip("\"'")
    raise RuntimeError(f"Dolo Herbert lock is missing {key}")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_array_mutation_shape_stdout(stdout: str) -> tuple[frozenset[str], int, str]:
    try:
        value = ast.literal_eval(stdout.strip())
    except (SyntaxError, ValueError) as exc:
        raise RuntimeError(
            "Herbert array-mutation shape owner emitted unparsable stdout: "
            f"{stdout!r}"
        ) from exc
    if not isinstance(value, tuple) or len(value) != 5:
        raise RuntimeError(
            "Herbert array-mutation shape owner emitted invalid shape tuple: "
            f"{value!r}"
        )

    tag, keyword, void_marker, value_marker, call_count = value
    if tag != "array-mutation-shape-candidate":
        raise RuntimeError(
            "Herbert array-mutation shape owner emitted unexpected tag: "
            f"{tag!r}"
        )
    markers = {
        "void": void_marker,
        "value": value_marker,
    }
    invalid = {
        kind: marker
        for kind, marker in markers.items()
        if type(marker) is not int or marker not in {0, 1}
    }
    if invalid:
        details = ", ".join(
            f"{kind}={marker!r}" for kind, marker in sorted(invalid.items())
        )
        raise RuntimeError(
            "Herbert array-mutation shape owner returned invalid "
            f"do_admits_kind marker(s): {details}"
        )
    admitted = frozenset(kind for kind, marker in markers.items() if marker == 1)
    if not admitted <= _VALID_BUILTIN_KINDS:
        raise RuntimeError(
            "Herbert array-mutation shape owner returned invalid admit set: "
            f"{admitted!r}"
        )
    if type(call_count) is not int:
        raise RuntimeError(
            "Herbert array-mutation shape owner returned non-integer "
            f"do_statement_call_count: {call_count!r}"
        )
    if type(keyword) is not str or not keyword:
        raise RuntimeError(
            "Herbert array-mutation shape owner returned invalid "
            f"do_statement_keyword: {keyword!r}"
        )
    return admitted, call_count, keyword


def _subprocess_summary(result: subprocess.CompletedProcess[str]) -> str:
    return (
        f"returncode={result.returncode}, "
        f"stdout={_first_line(result.stdout)!r}, "
        f"stderr={_first_line(result.stderr)!r}"
    )


def _first_line(text: str) -> str:
    return text.splitlines()[0] if text else ""


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
        if text.startswith("==", index):
            tokens.append(_HerbertToken("PUNCT", "==", line, column))
            index += 2
            column += 2
            continue
        if ch in "(),:+-=":
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
(
    _ARRAY_MUTATION_DO_ADMIT_KINDS,
    _ARRAY_MUTATION_DO_CALL_COUNT,
    _ARRAY_MUTATION_DO_KEYWORD,
) = load_array_mutation_shape()
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
        if value < 0:
            return None
        return value
    return None


def array_mutation_do_admits(kind: str | None) -> bool:
    return kind in _ARRAY_MUTATION_DO_ADMIT_KINDS


def array_mutation_do_call_count() -> int:
    return _ARRAY_MUTATION_DO_CALL_COUNT


def array_mutation_do_keyword() -> str:
    return _ARRAY_MUTATION_DO_KEYWORD


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

    delimiters = _seed_string_value_map(
        repo_root, owner_text, "closing_delimiter", "Dolo closing-delimiter owner"
    )
    if not delimiters:
        raise RuntimeError(
            f"Dolo closing-delimiter owner declares no delimiter data: {DOLO_CLOSING_DELIMITER_OWNER}"
        )
    return delimiters


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

    ops = _seed_marker_set(
        repo_root, owner_text, "infix_operator", "Dolo infix-operator owner"
    )
    if not ops:
        raise RuntimeError(
            f"Dolo infix-operator owner marks no recognized operators: {DOLO_INFIX_OPERATOR_OWNER}"
        )
    return ops


_DOLO_INFIX_OPERATORS_BY_OWNER = load_dolo_infix_operators()
def is_dolo_infix_operator(name: str) -> bool:
    return name in _DOLO_INFIX_OPERATORS_BY_OWNER
