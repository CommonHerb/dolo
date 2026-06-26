from __future__ import annotations

from pathlib import Path


DOLO_BOOLEAN_OPERATOR_OWNER = "experiments/herbert/boolean_operator_candidate.herb"
HERBERT_BUILTIN_ARITY_OWNER = "experiments/herbert/builtin_arity_candidate.herb"
HERBERT_BUILTIN_KIND_OWNER = "experiments/herbert/builtin_kind_candidate.herb"
HERBERT_TYPE_NAME_OWNER = "experiments/herbert/type_name_candidate.herb"
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


_DOLO_BOOLEAN_OPERATOR_LOWERINGS_BY_OWNER = load_dolo_boolean_operator_lowerings()
_HERBERT_BUILTIN_ARITIES_BY_OWNER = load_herbert_builtin_arities()
_HERBERT_BUILTIN_KINDS_BY_OWNER = load_herbert_builtin_kinds()
_HERBERT_TYPE_NAMES_BY_OWNER = load_herbert_type_names()
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


def herbert_builtin_arity(name: str) -> int | None:
    return _HERBERT_BUILTIN_ARITIES_BY_OWNER.get(name)


def herbert_builtin_kind(name: str) -> str | None:
    return _HERBERT_BUILTIN_KINDS_BY_OWNER.get(name)


def is_herbert_type_name(name: str) -> bool:
    return name in _HERBERT_TYPE_NAMES_BY_OWNER
