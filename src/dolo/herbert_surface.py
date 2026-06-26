from __future__ import annotations


DOLO_BOOLEAN_OPERATOR_LOWERINGS = {
    "!": "not",
    "&&": "and",
    "||": "or",
}
HERBERT_VALUE_BUILTINS = frozenset(
    {
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
HERBERT_VOID_BUILTINS = frozenset({"add", "append"})
HERBERT_BUILTINS = HERBERT_VALUE_BUILTINS | HERBERT_VOID_BUILTINS
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
