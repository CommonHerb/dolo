from __future__ import annotations


DOLO_BOOLEAN_OPERATOR_LOWERINGS = {
    "!": "not",
    "&&": "and",
    "||": "or",
}
HERBERT_BUILTIN_KINDS = {
    "add": "void",
    "append": "void",
    "count": "value",
    "equal": "value",
    "freeze": "value",
    "get": "value",
    "index": "value",
    "length": "value",
    "new_array": "value",
    "new_buffer": "value",
}
HERBERT_VALUE_BUILTINS = frozenset(
    name for name, kind in HERBERT_BUILTIN_KINDS.items() if kind == "value"
)
HERBERT_VOID_BUILTINS = frozenset(
    name for name, kind in HERBERT_BUILTIN_KINDS.items() if kind == "void"
)
HERBERT_BUILTINS = frozenset(HERBERT_BUILTIN_KINDS)
HERBERT_BUILTIN_ARITIES = {
    "add": 2,
    "append": 2,
    "count": 1,
    "equal": 2,
    "freeze": 1,
    "get": 2,
    "index": 2,
    "length": 1,
    "new_array": 1,
    "new_buffer": 0,
}
HERBERT_TYPE_NAMES = frozenset({"bool", "buffer", "int", "string"})
