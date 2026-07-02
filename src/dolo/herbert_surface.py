from __future__ import annotations

import ast
from functools import lru_cache
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




def _seed_owner_prefix_any(owner_text: str, label: str) -> str:
    """Like _seed_owner_prefix, but tolerates an owner with no main() of its own (the
    oracle's substituted owners declare only the algorithm). The boundary appends its
    own query main() either way."""
    match = re.search(r"(?m)^\s*func\s+main\s*\(", owner_text)
    if match is None:
        return owner_text
    return owner_text[: match.start()]


# The seed renders main()'s integer return as UNSIGNED 64-bit (0 - 1 prints as
# 18446744073709551615); decode two's-complement so an owner's negative not-found
# convention survives the wire. This is wire-format decoding (the same class as the
# ast.literal_eval on table stdout), not a Python-owned decision.
_SEED_UINT64_BOUND = 1 << 64
_SEED_INT64_MAX = (1 << 63) - 1


def seed_field_index(
    repo_root: Path,
    owner_text: str,
    fields: tuple[str, ...],
    name: str,
    label: str,
) -> int:
    """Compute field_index(fields, name) BY EXECUTING the owner on the pinned seed.

    The boundary embeds the query into a generated main() -- build the fields array,
    return one int (1 render word, under the seed's 15-word cap) -- then compiles+runs
    it through the seed and decodes stdout. Fail-closed throughout; no Python fallback."""
    prefix = _seed_owner_prefix_any(owner_text, label)
    lines = ["func main():", "    let fields = new_array(string)"]
    for field in fields:
        lines.append(f"    do add(fields, {_herb_string_literal(field)})")
    lines.append(f"    return field_index(fields, {_herb_string_literal(name)})")
    lines.append("end")
    program = prefix + "\n".join(lines) + "\n"
    stdout = _run_owner_program_on_seed(repo_root, program, label)
    try:
        value = ast.literal_eval(stdout.strip())
    except (SyntaxError, ValueError) as exc:
        raise RuntimeError(f"{label} emitted unparsable stdout: {stdout!r}") from exc
    if type(value) is not int or value < 0 or value >= _SEED_UINT64_BOUND:
        raise RuntimeError(
            f"{label} field_index returned a non-uint64 value: {value!r}"
        )
    if value > _SEED_INT64_MAX:
        value -= _SEED_UINT64_BOUND
    return value


_RFI_SMOKE_FIELDS = ("__dolo_smoke_a", "__dolo_smoke_b")


def load_record_field_index_owner_text(
    root: Path | str | None = None,
    *,
    smoke: bool = True,
) -> str:
    """Read + validate the record-field-index owner, fail-closed: it must declare
    field_index and (with smoke=True, the compiler's import-time contract) be
    executable by the pinned seed NOW -- one smoke query, ANY int accepted, since an
    owner's index semantics are its own. A missing/blank/garbage owner or seed makes
    the compiler unimportable, matching the other seed-executed authorities."""
    repo_root = Path(root) if root is not None else _REPO_ROOT
    owner_path = repo_root / RECORD_FIELD_INDEX_OWNER
    try:
        owner_text = owner_path.read_text()
    except OSError as exc:
        raise RuntimeError(
            f"Herbert record-field-index owner is unreadable: {RECORD_FIELD_INDEX_OWNER}"
        ) from exc
    if not _herbert_text_declares_function(owner_text, "field_index"):
        raise RuntimeError(
            f"Herbert record-field-index owner declares no field_index: "
            f"{RECORD_FIELD_INDEX_OWNER}"
        )
    if smoke:
        seed_field_index(
            repo_root,
            owner_text,
            _RFI_SMOKE_FIELDS,
            _RFI_SMOKE_FIELDS[-1],
            "Herbert record-field-index owner",
        )
    return owner_text


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




_DOLO_BOOLEAN_OPERATOR_LOWERINGS_BY_OWNER = load_dolo_boolean_operator_lowerings()
_DOLO_TWO_CHAR_OPS_BY_OWNER = load_dolo_two_char_ops()
_HERBERT_BUILTIN_ARITIES_BY_OWNER = load_herbert_builtin_arities()
_HERBERT_BUILTIN_KINDS_BY_OWNER = load_herbert_builtin_kinds()
_HERBERT_TYPE_NAMES_BY_OWNER = load_herbert_type_names()
_RECORD_FIELD_INDEX_OWNER_TEXT = load_record_field_index_owner_text()
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


@lru_cache(maxsize=None)
def _record_field_index_by_seed(fields: tuple[str, ...], name: str) -> int:
    return seed_field_index(
        _REPO_ROOT,
        _RECORD_FIELD_INDEX_OWNER_TEXT,
        fields,
        name,
        "Herbert record-field-index owner",
    )


def record_field_index(fields: tuple[str, ...], name: str) -> int | None:
    value = _record_field_index_by_seed(tuple(fields), name)
    if value < 0:
        return None
    return value


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
