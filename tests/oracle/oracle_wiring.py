#!/usr/bin/env python3
"""Held-back WIRING ORACLE for the Dolo sovereignty meter. ORCHESTRATOR-OWNED.

Codex (and any worker) MUST NOT edit anything under tests/oracle/ (see AGENTS.md and
this directory's README). This file is the grader; a worker cannot author the grader
it is judged by.

This module is deliberately NOT named test_*.py, so `unittest discover -p 'test_*.py'`
(the CI suite) does NOT pick it up. It is invoked explicitly by scripts/sovereignty_meter.sh.

Per authority, it proves a claimed Herbert-family replacement is GENUINELY WIRED -- the
Python owner is no longer load-bearing -- and is not a mirror, not a moved literal:

  CHECK-1  POISON-PYTHON: corrupt the Python-owned decision in dolo.herbert_surface
           BEFORE the compiler imports it, compile the held-back probe, and require the
           output to STILL match the held-back golden. If the emitter still consults the
           Python decision, the poison flips the output  ->  NOT WIRED.
  CHECK-2  REMOVE-OWNER (mandatory): a status=herbert flip MUST declare a herbert_owner that is
           a .herb under experiments/herbert/; blanking it must BREAK compilation -- proving the
           Herbert-family owner is load-bearing. Closes the "moved the Python literal into a
           renamed dict/helper" forge that the name-based CHECK-1 cannot see (cross-model audit).
  CHECK-3  SEMANTIC-PERTURBATION (orchestrator review, not yet automated): perturbing the
           owner's CONTENT (e.g. flip new_array->void in the .herb) must change the emitted
           output in the predicted direction -- proving the owner's CONTENT drives the decision,
           not merely that the file is load-bearing. The orchestrator authors+runs this at slice
           review until the owner format is fixed enough to automate (cross-model audit rec).

Usage:
  oracle_wiring.py <authority> [--bite-check]
    (default)     exit 0 = WIRED (both checks pass); 1 = NOT WIRED; 2 = no oracle authored
    --bite-check  exit 0 = the oracle BITES (poison breaks the CURRENT compiler); 1 = toothless.
                  Run this to PROVE the gate has teeth before arming a slice.
"""
from __future__ import annotations
import os, sys, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]       # tests/oracle/ -> repo root
SRC = ROOT / "src"
ORACLE = ROOT / "tests" / "oracle"
LEDGER = ROOT / "docs" / "sovereignty" / "ledger.tsv"

# The poison PATCH corrupts ONLY the named authority, applied AFTER the compiler is imported
# (so it lands no matter what the dolo package __init__ pulls in), by rewriting the Python-owned
# decision wherever it is currently bound across the dolo.* modules. A genuine Herbert-family
# owner is immune (the emitter no longer reads these names). Empty patch = no poison.
POISON = {
    # swap value<->void everywhere the kind sets are bound: a value built-in (new_array) becomes
    # "void" -> the genuine emitter rejects `let a = new_array(...)` ("has no value"); a
    # Herbert-wired emitter that no longer consults these sets is unaffected.
    "builtin_kind": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    _v=getattr(_m,'HERBERT_VALUE_BUILTINS',None); _o=getattr(_m,'HERBERT_VOID_BUILTINS',None)\n"
        "    if _v is not None and _o is not None:\n"
        "        _m.HERBERT_VALUE_BUILTINS=_o; _m.HERBERT_VOID_BUILTINS=_v\n"
        "    if hasattr(_m,'HERBERT_BUILTIN_KINDS'):\n"
        "        _m.HERBERT_BUILTIN_KINDS={_k:('void' if _x=='value' else 'value') for _k,_x in _m.HERBERT_BUILTIN_KINDS.items()}\n"
    ),
    # +1 to every built-in arity: new_array's poisoned arity (1->2) makes the genuine emitter reject
    # `new_array(string)` ("expects 2 arguments, got 1"); a Herbert-wired emitter is unaffected.
    "builtin_arity": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    _a=getattr(_m,'HERBERT_BUILTIN_ARITIES',None)\n"
        "    if isinstance(_a,dict):\n"
        "        _m.HERBERT_BUILTIN_ARITIES={_k:_v+1 for _k,_v in _a.items()}\n"
    ),
    # swap &&<->|| and force !->or: a probe using && / || / ! lowers to DIFFERENT Herbert text.
    "boolean_operator": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    _t=getattr(_m,'DOLO_BOOLEAN_OPERATOR_LOWERINGS',None)\n"
        "    if _t is not None:\n"
        "        _w=dict(_t)\n"
        "        if '&&' in _w and '||' in _w: _w['&&'],_w['||']=_w['||'],_w['&&']\n"
        "        if '!' in _w: _w['!']='or'\n"
        "        _m.DOLO_BOOLEAN_OPERATOR_LOWERINGS=_w\n"
    ),
    # empty the type-name set: the genuine emitter then rejects every `new_array(<type>)`.
    "type_name": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    if hasattr(_m,'HERBERT_TYPE_NAMES'):\n"
        "        _m.HERBERT_TYPE_NAMES=frozenset()\n"
    ),
}
PROBE = {
    "builtin_kind":     ORACLE / "programs" / "kind_probe.dolo",
    "builtin_arity":    ORACLE / "programs" / "arity_probe.dolo",
    "boolean_operator": ORACLE / "programs" / "boolean_probe.dolo",
    "type_name":        ORACLE / "programs" / "type_probe.dolo",
}
GOLDEN = {
    "builtin_kind":     ORACLE / "golden" / "kind_probe.herb",
    "builtin_arity":    ORACLE / "golden" / "arity_probe.herb",
    "boolean_operator": ORACLE / "golden" / "boolean_probe.herb",
    "type_name":        ORACLE / "golden" / "type_probe.herb",
}
# CHECK-3 (semantic perturbation): once an authority is wired, perturbing the owner's CONTENT must
# change the emitted output -- proving the owner's content DRIVES the decision (not just load-bearing).
# Per authority: (owner repo-path, the if/equal target name, the replacement return line).
PERTURB = {
    "builtin_kind":     ("experiments/herbert/builtin_kind_candidate.herb",  "new_array", 'return "void"'),
    "builtin_arity":    ("experiments/herbert/builtin_arity_candidate.herb", "count",     "return 2"),
    "boolean_operator": ("experiments/herbert/boolean_operator_candidate.herb", "&&",     'return "or"'),
    "type_name":        ("experiments/herbert/type_name_candidate.herb",     "string",    "return 0"),
}


def _compile(patch: str, probe: pathlib.Path):
    # import the compiler FIRST, then apply the poison patch, then compile -- so the patch lands
    # regardless of dolo's package import order. emit_program reads its module globals at call time.
    code = (
        "import sys\nfrom dolo.compiler import compile_source\n"
        + patch +
        "sys.stdout.write(compile_source(open(sys.argv[1]).read()))\n"
    )
    env = dict(os.environ, PYTHONPATH=str(SRC))
    r = subprocess.run([sys.executable, "-c", code, str(probe)],
                       env=env, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def _ledger_owner(auth: str):
    if not LEDGER.exists():
        return None
    for line in LEDGER.read_text().splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("id\t"):
            continue
        f = line.split("\t")
        if len(f) >= 5 and f[0] == auth and f[1] == "herbert" and f[4].strip():
            return f[4].strip()
    return None


def _compile_without_owner(owner_rel: str, probe: pathlib.Path):
    """Blank the declared herbert_owner file, compile, restore. Proves it is load-bearing."""
    p = ROOT / owner_rel
    if not p.exists():
        return None  # owner declared but missing -> caller treats as not-load-bearing
    backup = p.read_bytes()
    try:
        p.write_text("")  # neutralize the claimed Herbert owner
        return _compile("", probe)
    finally:
        p.write_bytes(backup)


def _perturb_owner_drives(auth: str, probe: pathlib.Path, golden: str) -> bool:
    """CHECK-3: perturb the owner's CONTENT; the probe output MUST change -- proving the owner's
       content DRIVES the decision, not merely that the file is load-bearing. Restores the owner."""
    cfg = PERTURB.get(auth)
    if not cfg:
        return True  # no perturbation configured -> do not block
    owner_rel, target, new_return = cfg
    p = ROOT / owner_rel
    if not p.exists():
        return True  # a missing owner is CHECK-2's job
    backup = p.read_bytes()
    lines = p.read_text().splitlines()
    flipped = False
    for i in range(len(lines) - 1):
        if f'if equal(name, "{target}"):' in lines[i] and lines[i + 1].lstrip().startswith("return "):
            indent = lines[i + 1][: len(lines[i + 1]) - len(lines[i + 1].lstrip())]
            lines[i + 1] = indent + new_return
            flipped = True
            break
    if not flipped:
        return False  # the target entry is not in the owner -> content does not drive it (or wrong format)
    try:
        p.write_text("\n".join(lines) + "\n")
        rc, out, _ = _compile("", probe)
        return not (rc == 0 and out == golden)  # the output MUST differ from the golden
    finally:
        p.write_bytes(backup)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__); return 2
    auth = sys.argv[1]
    bite = "--bite-check" in sys.argv[2:]
    if auth not in POISON:
        print(f"oracle: no held-back oracle authored for '{auth}' yet", file=sys.stderr); return 2
    golden = GOLDEN[auth].read_text()

    # CHECK-1: poison the Python owner, compile, compare to the held-back golden.
    rc, out, err = _compile(POISON[auth], PROBE[auth])
    poison_is_noop = (rc == 0 and out == golden)

    if bite:
        if not poison_is_noop:
            print(f"BITE OK: poisoning '{auth}' breaks the current (Python-owned) compiler "
                  f"-> the oracle has teeth (a fake/mirror wiring would be caught).")
            return 0
        print(f"TOOTHLESS: poisoning '{auth}' had NO effect -- the oracle would not catch a fake wiring.",
              file=sys.stderr)
        return 1

    if not poison_is_noop:
        print(f"NOT WIRED: '{auth}' still depends on the Python owner "
              f"(poisoning herbert_surface flips the emitted output) -> RED.")
        return 1

    # CHECK-2 (MANDATORY): a real wiring must name a LOAD-BEARING Herbert-family owner.
    # CHECK-1's poison is name-based, so a forge that moves the decision into a RENAMED Python
    # dict/helper would pass CHECK-1 falsely (cross-model audit caught this). Requiring a
    # load-bearing .herb owner closes it: such a forge has no Herbert owner whose blanking breaks
    # compilation. (CHECK-1 still matters: it proves the OLD Python authority is gone, not just
    # that a NEW Herbert one exists.)
    owner = _ledger_owner(auth)
    if not owner:
        print(f"NOT WIRED: '{auth}' is status=herbert but declares NO herbert_owner. A genuine "
              f"replacement must name a Herbert-family owner whose removal breaks compilation "
              f"(otherwise a renamed Python literal slips past the name-based CHECK-1) -> RED.")
        return 1
    if not (owner.startswith("experiments/herbert/") and owner.endswith(".herb")):
        print(f"NOT WIRED: herbert_owner '{owner}' is not a Herbert-family artifact "
              f"(must be a .herb under experiments/herbert/) -> RED.")
        return 1
    res = _compile_without_owner(owner, PROBE[auth])
    if res is None:
        print(f"NOT WIRED: declared herbert_owner '{owner}' is missing -> RED.")
        return 1
    rc2, out2, err2 = res
    if rc2 == 0 and out2 == golden:
        print(f"NOT WIRED: blanking the herbert_owner '{owner}' did NOT break compilation -- "
              f"the Herbert owner is not load-bearing (moved-literal / dead-dependency forge?) -> RED.")
        return 1

    # CHECK-3: the owner's CONTENT must drive the decision (perturb it -> output changes).
    if not _perturb_owner_drives(auth, PROBE[auth], golden):
        print(f"NOT WIRED: perturbing the herbert_owner's content did not change the emitted output "
              f"-- the owner's CONTENT does not drive the decision (CHECK-3) -> RED.")
        return 1

    print(f"WIRED: '{auth}' -- Python neutralization is a no-op (old authority gone), the "
          f"Herbert-family owner '{owner}' is load-bearing, and its content drives the decision -> GREEN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
