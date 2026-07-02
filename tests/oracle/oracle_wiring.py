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
    # empty the lexer's two-char-op set: `1 == 2` then lexes as `1,=,=,2` and the emitter rejects the bare `=`.
    "two_char_ops": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    if hasattr(_m,'TWO_CHAR_OPS'):\n"
        "        _m.TWO_CHAR_OPS=set()\n"
    ),
    # swap the parser's closer->opener mapping: a `(...)` expression then mismatches -> rejected.
    "closing_delimiters": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    _c=getattr(_m,'CLOSING_DELIMITERS',None)\n"
        "    if isinstance(_c,dict) and ')' in _c and '}' in _c:\n"
        "        _m.CLOSING_DELIMITERS={')':_c['}'],'}':_c[')']}\n"
    ),
    # empty the emitter's infix-operator set: an infix op in the probe is then unrecognized -> error.
    "infix_operators": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    if hasattr(_m,'INFIX_OPERATORS'):\n"
        "        _m.INFIX_OPERATORS=frozenset()\n"
    ),
    # empty the lexer's keyword set: record/fn/let/if/else/return/true then lex as IDENTs and the
    # parser rejects the probe. A genuine wiring consults the Herbert-family owner via the boundary
    # (no Python-owned KEYWORDS name left to poison), so it is unaffected.
    "lexer_keywords": (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        "    if hasattr(_m,'KEYWORDS'):\n"
        "        _m.KEYWORDS=set()\n"
    ),
}
PROBE = {
    "builtin_kind":     ORACLE / "programs" / "kind_probe.dolo",
    "builtin_arity":    ORACLE / "programs" / "arity_probe.dolo",
    "boolean_operator": ORACLE / "programs" / "boolean_probe.dolo",
    "type_name":        ORACLE / "programs" / "type_probe.dolo",
    "two_char_ops":      ORACLE / "programs" / "two_char_probe.dolo",
    "closing_delimiters":ORACLE / "programs" / "closing_delim_probe.dolo",
    "infix_operators":   ORACLE / "programs" / "infix_probe.dolo",
    "lexer_keywords":    ORACLE / "programs" / "keyword_probe.dolo",
}
GOLDEN = {
    "builtin_kind":     ORACLE / "golden" / "kind_probe.herb",
    "builtin_arity":    ORACLE / "golden" / "arity_probe.herb",
    "boolean_operator": ORACLE / "golden" / "boolean_probe.herb",
    "type_name":        ORACLE / "golden" / "type_probe.herb",
    "two_char_ops":      ORACLE / "golden" / "two_char_probe.herb",
    "closing_delimiters":ORACLE / "golden" / "closing_delim_probe.herb",
    "infix_operators":   ORACLE / "golden" / "infix_probe.herb",
    "lexer_keywords":    ORACLE / "golden" / "keyword_probe.herb",
}
# CHECK-3 (semantic perturbation): once an authority is wired, perturbing the owner's CONTENT must
# change the emitted output -- proving the owner's content DRIVES the decision (not just load-bearing).
# Per authority: (owner repo-path, the if/equal target name, the replacement return line).
PERTURB = {
    "builtin_kind":     ("experiments/herbert/builtin_kind_candidate.herb",  "new_array", 'return "void"'),
    "builtin_arity":    ("experiments/herbert/builtin_arity_candidate.herb", "count",     "return 2"),
    "boolean_operator": ("experiments/herbert/boolean_operator_candidate.herb", "&&",     'return "or"'),
    "type_name":        ("experiments/herbert/type_name_candidate.herb",     "string",    "return 0"),
    "two_char_ops":      ("experiments/herbert/two_char_ops_candidate.herb",  "==",        "return 0"),
    "closing_delimiters":("experiments/herbert/closing_delimiters_candidate.herb", ")",    'return "{"'),
    "infix_operators":   ("experiments/herbert/infix_operators_candidate.herb", "==",      "return 0"),
    "lexer_keywords":    ("experiments/herbert/lexer_keywords_candidate.herb", "let",      "return 0"),
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
    if auth in COMPUTATION_AUTHORITIES:
        # record_field_index / array_mutation are per-program COMPUTATION/SHAPE authorities; the
        # static-table POISON path cannot grade them. Route to the dedicated graders (below).
        return _grade_computation(auth, bite)
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


# ============================================================================
# COMPUTATION / SHAPE AUTHORITY GRADERS  (record_field_index, array_mutation)
# ----------------------------------------------------------------------------
# These two authorities are NOT static global tables: they are per-program
# COMPUTATIONS (record_field_index = field-name -> positional index; array_mutation
# = the do-statement lowering SHAPE: void-gating + exactly-one-call + keyword).
# The 7-id POISON table path above cannot grade them, so they get dedicated
# graders. TRUTH is computed IN-ORACLE (closed-form from oracle-generated owner
# templates / oracle-computed positions) -- no worker-touchable golden/fixture/
# manifest is consulted for the VALUE, so lockstep edits cannot move this oracle.
# ============================================================================
import re as _re
import random as _random
import tempfile as _tempfile

COMPUTATION_AUTHORITIES = {"record_field_index", "array_mutation"}
PROG = ORACLE / "programs"
FIELD_IDX = _re.compile(r"(?<=\w)\.(\d+)\b")     # the N in a `var.N` field-access lowering


def _grade_computation(auth: str, bite: bool) -> int:
    # Seeded for REPRODUCIBILITY (a RED is re-runnable) while staying author-UNKNOWN per run:
    # default = fresh entropy each invocation (a worker cannot pre-compute the draws to overfit), and
    # a GENUINE wiring passes for EVERY seed, so this never false-flakes -- a red is always a real bug,
    # now reproducible. DOLO_ORACLE_SEED pins the seed (repro / deterministic debugging).
    # (cross-model audit, Codex gpt-5.5 + completeness critic: seed-and-print the RNG.)
    _env = os.environ.get("DOLO_ORACLE_SEED")
    _seed = int(_env) if _env else int.from_bytes(os.urandom(8), "big")
    print(f"[oracle] {auth} seed={_seed} (re-run with DOLO_ORACLE_SEED={_seed} to reproduce)",
          file=sys.stderr)
    rng = _random.Random(_seed)
    if auth == "record_field_index":
        return _grade_record_field_index(rng, bite)
    return _grade_array_mutation(rng, bite)


def _indexes(text: str):
    return [int(m) for m in FIELD_IDX.findall(text)]


def _emit(patch: str, source: str):
    """Compile a SYNTHESIZED .dolo source string via compile_source; return (rc, indexes, out)."""
    fd, name = _tempfile.mkstemp(suffix=".dolo")
    os.close(fd)
    probe = pathlib.Path(name)
    try:
        probe.write_text(source)
        rc, out, err = _compile(patch, probe)
    finally:
        probe.unlink()
    return rc, _indexes(out), out


def _install(rel: str, text: str):
    """Overwrite an owner file with `text`; return a restore() closure (call in finally)."""
    p = ROOT / rel
    backup = p.read_bytes()
    p.write_text(text)
    return lambda: p.write_bytes(backup)


def _other_row_owners(auth: str) -> set[str]:
    """Anti-laundering: every OTHER status=herbert row's herbert_owner."""
    owners: set[str] = set()
    if not LEDGER.exists():
        return owners
    for line in LEDGER.read_text().splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("id\t"):
            continue
        f = line.split("\t")
        if len(f) >= 6 and f[0] not in ("id", auth) and f[1] == "herbert" and f[4].strip():
            owners.add(f[4].strip())
    return owners


# ----------------------------------------------------------------------------
# record_field_index  --  EXECUTION-EQUIVALENCE grader
# ----------------------------------------------------------------------------
# GREEN only when the live emitter computes the field index by EXECUTING the
# on-disk owner's algorithm (the pinned seed compiles+runs the owner per query),
# so the emitted value tracks owner perturbations -- step!=1 and a content-weighted
# accumulator -- that no finite-scalar `.index`+offset shim can mimic. The
# substituted owners below use ONLY the seed-native subset (count/get/infix +
# recursion) so the pinned seed can execute every one of them.
RFI_OWNER_DEFAULT = "experiments/herbert/record_field_index_candidate.herb"
RFI_NOT_FOUND = 9999
RFI_K = 30
SENTINELS = (90001, 90002)

_NAME_POOL = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray",
]

RFI_FIXED = [
    (PROG / "rfi_probe.dolo", [1, 2, 1, 2, 0]),
    (PROG / "rfi_probe2.dolo", [0, 2, 1, 3]),
]


def _herb_base(b):
    text = (
        "func field_index(fields, name):\n"
        f"    return search(fields, name, 0, {b})\n"
        "end\n\n"
        "func search(fields, name, i, acc):\n"
        "    if i == count(fields):\n"
        f"        return {RFI_NOT_FOUND}\n"
        "    else:\n"
        "        if equal(get(fields, i), name):\n"
        "            return acc\n"
        "        else:\n"
        "            return search(fields, name, i + 1, acc + 1)\n"
        "        end\n"
        "    end\n"
        "end\n"
    )
    return text, (lambda F, n: b + list(F).index(n))


def _herb_step(b, s):
    text = (
        "func field_index(fields, name):\n"
        f"    return search(fields, name, 0, {b})\n"
        "end\n\n"
        "func search(fields, name, i, acc):\n"
        "    if i == count(fields):\n"
        f"        return {RFI_NOT_FOUND}\n"
        "    else:\n"
        "        if equal(get(fields, i), name):\n"
        "            return acc\n"
        "        else:\n"
        f"            return search(fields, name, i + 1, acc + {s})\n"
        "        end\n"
        "    end\n"
        "end\n"
    )
    return text, (lambda F, n: b + s * list(F).index(n))


def _herb_weighted(b, s, heavy):
    text = (
        "func field_index(fields, name):\n"
        f'    return search(fields, name, 0, {b}, "{heavy}", {s})\n'
        "end\n\n"
        "func search(fields, name, i, acc, heavy, s):\n"
        "    if i == count(fields):\n"
        f"        return {RFI_NOT_FOUND}\n"
        "    else:\n"
        "        if equal(get(fields, i), name):\n"
        "            return acc\n"
        "        else:\n"
        "            if equal(get(fields, i), heavy):\n"
        "                return search(fields, name, i + 1, acc + s, heavy, s)\n"
        "            else:\n"
        "                return search(fields, name, i + 1, acc + 1, heavy, s)\n"
        "            end\n"
        "        end\n"
        "    end\n"
        "end\n"
    )

    def ans(F, n):
        F = list(F)
        r = F.index(n)
        bonus = (s - 1) if heavy in F[:r] else 0
        return b + r + bonus

    return text, ans


def _herb_multiweight(b, wmap):
    # A VARIABLE-STRUCTURE family: each step adds weight(field) via a per-field weight() table
    # (a random subset of fields carry a random weight; the rest weigh 1). A finite Python
    # template-matcher (base/step/single-heavy) cannot pre-port an arbitrary weight table -- only a
    # GENERIC evaluator that runs weight() per field tracks it.
    lines = [
        "func field_index(fields, name):",
        f"    return search(fields, name, 0, {b})",
        "end",
        "",
        "func search(fields, name, i, acc):",
        "    if i == count(fields):",
        f"        return {RFI_NOT_FOUND}",
        "    else:",
        "        if equal(get(fields, i), name):",
        "            return acc",
        "        else:",
        "            return search(fields, name, i + 1, acc + weight(get(fields, i)))",
        "        end",
        "    end",
        "end",
        "",
        "func weight(f):",
    ]
    indent = "    "
    for h, w in wmap.items():
        lines.append(f'{indent}if equal(f, "{h}"):')
        lines.append(f"{indent}    return {w}")
        lines.append(f"{indent}else:")
        indent += "    "
    lines.append(f"{indent}return 1")
    for _ in wmap:
        indent = indent[:-4]
        lines.append(f"{indent}end")
    lines.append("end")
    text = "\n".join(lines) + "\n"

    def ans(F, n):
        F = list(F)
        r = F.index(n)
        return b + sum(wmap.get(F[i], 1) for i in range(r))

    return text, ans


def _synth(records, accesses):
    lines = []
    for rname, fields in records.items():
        lines.append("record " + rname + " { " + ", ".join(fields) + " }")
    lines.append("fn main() {")
    seen = set()
    for (v, r, f) in accesses:
        if v not in seen:
            args = ", ".join(str(i + 1) for i in range(len(records[r])))
            lines.append(f"  let {v} = {r}({args})")
            seen.add(v)
    tup = ", ".join(f"{v}.{f}" for (v, r, f) in accesses)
    lines.append(f"  return ({tup})")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _distinct_names(rng, k):
    return rng.sample(_NAME_POOL, k)


def _rfi_collision(rng):
    k = rng.randint(2, 5)
    a = _distinct_names(rng, k)
    q = rng.choice(a)
    b = a[:]
    while b.index(q) == a.index(q):
        rng.shuffle(b)
    records = {"Arec": tuple(a), "Brec": tuple(b)}
    accesses = [("a", "Arec", q), ("b", "Brec", q)]
    for f in rng.sample(a, min(2, k)):
        accesses.append(("a", "Arec", f))
    return records, accesses


def _rfi_single(rng):
    k = rng.randint(2, 6)
    a = _distinct_names(rng, k)
    return {"Arec": tuple(a)}, [("a", "Arec", f) for f in a]


def _override_patch(s):
    return (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if getattr(_m,'__name__','').startswith('dolo') and hasattr(_m,'record_field_index'):\n"
        f"        _m.record_field_index=(lambda *a,**k: {s})\n"
    )


def _rfi_check1(rel, rng):
    """CHECK-1 OVERRIDE-BOUNDARY: the emitted index is SOURCED from the named boundary (Python dead)."""
    text, _ = _herb_base(0)
    restore = _install(rel, text)
    try:
        records, accesses = _rfi_collision(rng)
        src = _synth(records, accesses)
        rc0, idx0, out0 = _emit("", src)
        if rc0 != 0 or not idx0:
            return False
        outs = []
        for s in SENTINELS:
            rc, idx, out = _emit(_override_patch(s), src)
            if rc != 0 or not idx or any(v != s for v in idx) or out == out0:
                return False
            outs.append(out)
        return outs[0] != outs[1]
    finally:
        restore()


def _rfi_checkR(rel, rng, trials=RFI_K):
    """CHECK-R randomized correctness + collision over the WORKER'S owner (kills static/overfit tables)."""
    for _ in range(trials):
        records, accesses = _rfi_collision(rng)
        rc, idx, out = _emit("", _synth(records, accesses))
        expected = [list(records[r]).index(f) for (_v, r, f) in accesses]
        if rc != 0 or idx != expected:
            return False
    return True


RFI_FAMILIES = ("base", "step", "weighted", "multiweight")


def _gen_xform(rng, fam=None):
    fam = fam or rng.choice(RFI_FAMILIES)
    b = rng.randint(0, 3)
    if fam == "base":
        text, ans = _herb_base(b)
        recs, accs = _rfi_single(rng)
        return text, ans, recs, accs
    if fam == "step":
        s = rng.randint(2, 5)
        text, ans = _herb_step(b, s)
        recs, accs = _rfi_single(rng)
        return text, ans, recs, accs
    if fam == "weighted":
        s = rng.randint(2, 5)
        k = rng.randint(3, 6)
        names = _distinct_names(rng, k)
        heavy = names[0]                   # heavy at position 0 -> bonus exposed at rank>=1
        text, ans = _herb_weighted(b, s, heavy)
        return text, ans, {"Arec": tuple(names)}, [("a", "Arec", f) for f in names]
    # multiweight: a random subset of fields carry random weights (variable structure)
    k = rng.randint(3, 6)
    names = _distinct_names(rng, k)
    heavy_count = rng.randint(1, max(1, k - 1))
    heavies = names[:heavy_count]          # the leading fields carry weights -> precede later targets
    wmap = {h: rng.randint(2, 5) for h in heavies}
    text, ans = _herb_multiweight(b, wmap)
    return text, ans, {"Arec": tuple(names)}, [("a", "Arec", f) for f in names]


def _rfi_checkX(rel, rng, trials=RFI_K):
    """CHECK-X SUBSTITUTED-OWNER EXECUTION EQUIVALENCE (keystone): the live value must equal the
       oracle's closed-form evaluation of an oracle-GENERATED owner. The family spans base /
       step!=1 / single-heavy / VARIABLE-STRUCTURE multiweight; the multiweight member (a random
       per-field weight table) cannot be pre-ported by a finite Python template-matcher, so only a
       GENERIC owner evaluator passes. Every family is covered at least once per run."""
    # deterministically cover each family first, then random for the remainder
    schedule = list(RFI_FAMILIES) + [None] * max(0, trials - len(RFI_FAMILIES))
    for fam in schedule:
        text, ans, recs, accs = _gen_xform(rng, fam)
        restore = _install(rel, text)
        try:
            rc, idx, out = _emit("", _synth(recs, accs))
            expected = [ans(recs[r], f) for (_v, r, f) in accs]
            if rc != 0 or idx != expected:
                return False
        finally:
            restore()
    return True


def _cosmetic_rewrite(text, rng):
    new = "acc" + str(rng.randint(100, 999))
    out = _re.sub(r"\bacc\b", new, text)
    out = out.replace("\nend\n", "\nend\n\n")
    return out


def _rfi_checkC(rel, rng, trials=8):
    """CHECK-C COSMETIC REWRITE of the worker's own owner -> shipped semantics still emit true positions."""
    base = (ROOT / rel).read_text()
    for _ in range(trials):
        restore = _install(rel, _cosmetic_rewrite(base, rng))
        try:
            recs, accs = _rfi_single(rng)
            rc, idx, out = _emit("", _synth(recs, accs))
            expected = [list(recs[r]).index(f) for (_v, r, f) in accs]
            if rc != 0 or idx != expected:
                return False
        finally:
            restore()
    return True


_RFI_STATIC_MIRROR = (
    "func field_index(fields, name):\n"
    '    if equal(name, "alpha"):\n'
    "        return 0\n"
    "    else:\n"
    '        if equal(name, "bravo"):\n'
    "            return 1\n"
    "        else:\n"
    f"            return {RFI_NOT_FOUND}\n"
    "        end\n"
    "    end\n"
    "end\n"
)


def _rfi_forge_leg(rel, rng):
    """Teeth self-test bound to the SHIM signature (not one file shape)."""
    restore = _install(rel, _RFI_STATIC_MIRROR)              # (a) static mirror -> CHECK-R must RED
    try:
        a = not _rfi_checkR(rel, rng, trials=8)
    finally:
        restore()
    text, ans = _herb_step(0, 2)                             # (b) SHIM-WITNESS: live MUST follow step=2
    restore = _install(rel, text)
    try:
        recs, accs = _rfi_single(rng)
        rc, idx, out = _emit("", _synth(recs, accs))
        plain = [list(recs[r]).index(f) for (_v, r, f) in accs]
        truth = [ans(recs[r], f) for (_v, r, f) in accs]
        b = (rc == 0 and idx == truth and idx != plain)
    finally:
        restore()
    c = (idx != [t + 1 for t in truth]) if truth else True   # (c) compare-sanity
    return a and b and c


# RESIDUAL (cross-model audit, Codex gpt-5.5; re-confirmed at the seed-execution reconcile):
# CHECK-X binds the emitted value to the oracle's closed-form over an owner family {base, step!=1,
# single-heavy, VARIABLE-STRUCTURE multiweight}. The multiweight member defeats a matcher that
# pre-ports only the scalar formulas, but the sharpened threat stands: these families are FINITE
# TEMPLATES, so a forge that regex-parses b/s/heavy AND the weight() if-chain into a dict passes
# every behavioral check without executing anything -- and no output-graded oracle can catch a
# perfect simulator, by construction. The genuine wiring now EXECUTES the owner on the PINNED SEED
# (the transfer this residual always pointed at, completed). The guard against a template-matcher
# or shadow-evaluator forge is therefore NOT behavioral: it is the reconcile doctrine's semantic
# source review -- the wiring may contain NO owner-text parsing beyond the sanctioned main()-strip
# in _seed_owner_prefix_any, and the orchestrator reads the diff before accepting any flip.
def _grade_record_field_index(rng, bite=False):
    if bite:
        if _rfi_forge_leg(RFI_OWNER_DEFAULT, rng):
            print("BITE OK: record_field_index forge-leg confirms teeth "
                  "(static mirror -> CHECK-R RED; step=2 SHIM-WITNESS divergence observed).")
            return 0
        print("TOOTHLESS: record_field_index forge-leg did not bite.", file=sys.stderr)
        return 1
    owner = _ledger_owner("record_field_index")
    if not owner or not (owner.startswith("experiments/herbert/") and owner.endswith(".herb")):
        print("NOT WIRED: 'record_field_index' is status=python or names no Herbert-family .herb "
              "owner under experiments/herbert/ -> RED.")
        return 1
    if owner in _other_row_owners("record_field_index"):
        print(f"NOT WIRED: owner {owner!r} is another row's already-paid owner (authority laundering) -> RED.")
        return 1
    res = _compile_without_owner(owner, RFI_FIXED[0][0])     # CHECK-2 load-bearing
    if res is None or res[0] == 0:
        print("NOT WIRED: blanking the herbert_owner did not break compilation "
              "(owner is not load-bearing for the index computation) -> RED.")
        return 1
    if not _rfi_check1(owner, rng):
        print("NOT WIRED: override-boundary failed -- the emitted index is not sourced from the named "
              "boundary (a parallel Python `.index` still produces the value) -> RED.")
        return 1
    if not _rfi_checkR(owner, rng):
        print("NOT WIRED: randomized correctness/collision failed (static/overfit table) -> RED.")
        return 1
    if not _rfi_checkC(owner, rng):
        print("NOT WIRED: cosmetic-rewrite equivalence failed (fingerprint fast-path) -> RED.")
        return 1
    if not _rfi_checkX(owner, rng):
        print("NOT WIRED: SUBSTITUTED-OWNER EXECUTION EQUIVALENCE failed -- the emitted index does not "
              "track the on-disk owner's ALGORITHM under step!=1 / content-weighted perturbation; a "
              "finite-scalar `.index`+offset shim cannot follow it -> RED.")
        return 1
    if not _rfi_forge_leg(owner, rng):
        print("NOT WIRED: forge-leg self-test did not confirm teeth -> RED.")
        return 1
    for probe, expected in RFI_FIXED:
        rc, idx, out = _emit("", probe.read_text())
        if rc != 0 or idx != expected:
            print(f"NOT WIRED: fixed held-back probe {probe.name} index mismatch "
                  f"(got {idx}, want {expected}) -> RED.")
            return 1
    print("WIRED: 'record_field_index' -- index sourced from the boundary, owner load-bearing + "
          "array_mutation-specific, and the owner's ALGORITHM drives the per-record index "
          "(step / content-weighted execution-equivalence) -> GREEN.")
    return 0


# ----------------------------------------------------------------------------
# array_mutation  --  do-statement lowering SHAPE grader
# ----------------------------------------------------------------------------
# Binds the do-statement SHAPE: void-gating admissibility (D4) + exactly-one-call
# (D5) + keyword (D1), each routed through a named owner-loaded poisonable binding.
# A keyword-only / scope-narrowed forge leaves D4/D5 inline -> the structural
# poison matrix rows for admit/call-count are no-ops -> RED.
AM_PROBE = PROG / "array_mutation_probe.dolo"
AM_GOLDEN = ORACLE / "golden" / "array_mutation_probe.herb"
AM_VALUE_DO = PROG / "array_mutation_value_do.dolo"
AM_TWOCALL = PROG / "array_mutation_twocall_do.dolo"
AM_DOLOFN = PROG / "array_mutation_dolofn_do.dolo"
AM_NONCALL = PROG / "array_mutation_noncall_do.dolo"
AM_STRUCT_PROBES = [(AM_VALUE_DO, "reject"), (AM_TWOCALL, "reject"),
                    (AM_DOLOFN, "reject"), (AM_NONCALL, "reject")]


def _poison_set(attr, val):
    return (
        "import sys as _s\n"
        "for _m in list(_s.modules.values()):\n"
        "    if not getattr(_m,'__name__','').startswith('dolo'): continue\n"
        f"    if hasattr(_m,'{attr}'): _m.{attr}={val}\n"
    )


def _am_matrix(golden):
    return [
        ("keyword",
         _poison_set("_ARRAY_MUTATION_DO_KEYWORD", "'POISONED_KW'"),
         AM_PROBE, lambda rc, out: rc == 0 and out != golden and "POISONED_KW" in out),
        ("admit-empty",
         _poison_set("_ARRAY_MUTATION_DO_ADMIT_KINDS", "frozenset()"),
         AM_PROBE, lambda rc, out: rc != 0),                          # do add now REJECTS
        ("admit-value",
         _poison_set("_ARRAY_MUTATION_DO_ADMIT_KINDS", "frozenset({'void','value'})"),
         AM_VALUE_DO, lambda rc, out: rc == 0),                       # do count now ACCEPTS
        ("callcount-reject",
         _poison_set("_ARRAY_MUTATION_DO_CALL_COUNT", "2"),
         AM_PROBE, lambda rc, out: rc != 0),                          # 1-call now REJECTS
        ("callcount-accept",
         _poison_set("_ARRAY_MUTATION_DO_CALL_COUNT", "2"),
         AM_TWOCALL, lambda rc, out: rc == 0),                        # 2-call now ACCEPTS
    ]


def _edit_owner_return(lines, anchor, new_return):
    for i in range(len(lines) - 1):
        if anchor in lines[i] and lines[i + 1].lstrip().startswith("return "):
            ind = lines[i + 1][: len(lines[i + 1]) - len(lines[i + 1].lstrip())]
            lines[i + 1] = ind + new_return
            return True
    return False


def _am_struct_differential(golden):
    owner = _ledger_owner("array_mutation")
    if not owner:
        return False
    p = ROOT / owner
    if not p.exists():
        return False
    base = p.read_text()
    cases = [
        ('if equal(kind, "void"):', "return 0", AM_PROBE, "reject"),
        ('if equal(kind, "value"):', "return 1", AM_VALUE_DO, "accept"),
        ("func do_statement_call_count", "return 2", AM_PROBE, "reject"),
        ("func do_statement_call_count", "return 2", AM_TWOCALL, "accept"),
    ]
    for anchor, newret, probe, want in cases:
        lines = base.splitlines()
        if not _edit_owner_return(lines, anchor, newret):
            return False                          # decision not in owner -> content cannot drive it
        try:
            p.write_text("\n".join(lines) + "\n")
            rc, out, _ = _compile("", probe)
        finally:
            p.write_text(base)
        if (want == "accept") != (rc == 0):
            return False
        if want == "reject" and probe == AM_PROBE and rc == 0 and out == golden:
            return False
    # KEYWORD content-perturbation (cross-model audit, Codex gpt-5.5): the do-statement KEYWORD must
    # be owner-SOURCED too, not merely poison-bound (CHECK-1 proves the binding is connected; this
    # proves the OWNER FILE's content drives the emitted keyword). Edit the owner's keyword return to
    # a sentinel; the EMITTED keyword must change to track it. A keyword-only moved literal (keyword
    # emitted from an inline Python constant while the owner is only poison-bound) leaves this RED.
    _KW = "doxx"
    lines = base.splitlines()
    if not _edit_owner_return(lines, "func do_statement_keyword", f'return "{_KW}"'):
        return False  # owner declares no keyword function -> the keyword is not owner-content-driven
    try:
        p.write_text("\n".join(lines) + "\n")
        rc, out, _ = _compile("", AM_PROBE)
    finally:
        p.write_text(base)
    if rc != 0 or _KW not in out or out == golden:
        return False
    return True


# RESIDUAL (cross-model audit, Codex gpt-5.5), shared by ALL require-move authorities, not just this one:
#   (1) ESCAPE-HATCH: a forge `if binding != DEFAULT: use_owner else: inline_python` keeps Python
#       load-bearing on the UNPOISONED path while every poison/edit (binding != DEFAULT) moves the
#       verdict. CHECK-1/CHECK-3 prove the binding is CONNECTED, not that the DEFAULT path is
#       binding-SOURCED; no behavioral poison distinguishes the two (binding==DEFAULT is a no-op).
#       CLOSED at reconcile, NOT here: the orchestrator must source-verify the inline do-policy is
#       DELETED (AGENTS.md earned-slice criterion #2, "remove the old path -> something breaks").
#   (2) SCOPE: D2 (call-required) and D3 (Dolo-fn rejection) verdicts are FORCED by CHECK-0 (the
#       baseline must reject `do a` / `do helper`), but they have no independent owner knob -- the
#       genuine wiring SUBSUMES them into call-count (D5) and admissibility (D4). Their mechanism is
#       not separately poison-bound; the authority is scoped to the SHAPE = D1 + D4 + D5.
def _grade_array_mutation(rng, bite=False):
    golden = AM_GOLDEN.read_text()
    matrix = _am_matrix(golden)
    if bite:
        for lbl, pat, prb, pred in matrix:
            rc, out, _ = _compile(pat, prb)
            if not pred(rc, out):
                print(f"TOOTHLESS: structural poison {lbl!r} is a no-op on the current compiler.",
                      file=sys.stderr)
                return 1
        print("BITE OK: every structural do-statement poison moves the verdict.")
        return 0
    # CHECK-0 baseline + negative-probe forcing (defeats the vacuous-constant / admit-all owner)
    rc, out, _ = _compile("", AM_PROBE)
    if not (rc == 0 and out == golden):
        print("NOT WIRED: baseline `do add` emit != golden -> RED.")
        return 1
    for prb, want in AM_STRUCT_PROBES:
        rc, _, _ = _compile("", prb)
        if (want == "reject") == (rc == 0):
            print(f"NOT WIRED: baseline verdict on {prb.name} is wrong (owner lacks the real do-shape "
                  f"policy / laundered constant) -> RED.")
            return 1
    # CHECK-1 structural poison matrix (every do-statement decision must be owner-driven)
    for lbl, pat, prb, pred in matrix:
        rc, out, _ = _compile(pat, prb)
        if not pred(rc, out):
            print(f"NOT WIRED: poisoning owner binding {lbl!r} did NOT move the verdict -- that "
                  f"do-statement decision is still Python (keyword-only / scope-narrowed forge) -> RED.")
            return 1
    # CHECK-2 owner load-bearing + anti-laundering owner-specificity
    owner = _ledger_owner("array_mutation")
    if not owner:
        print("NOT WIRED: 'array_mutation' is status=python / declares no herbert_owner -> RED.")
        return 1
    if not (owner.startswith("experiments/herbert/") and owner.endswith(".herb")):
        print("NOT WIRED: owner is not a .herb under experiments/herbert/ -> RED.")
        return 1
    if owner in _other_row_owners("array_mutation"):
        print(f"NOT WIRED: owner {owner!r} is another row's already-paid owner (authority laundering) -> RED.")
        return 1
    res = _compile_without_owner(owner, AM_PROBE)
    if res is None:
        print("NOT WIRED: declared herbert_owner is missing -> RED.")
        return 1
    if res[0] == 0:
        # Tightened to match record_field_index (cross-model audit, Codex gpt-5.5): a genuine
        # owner-driven do-policy must FAIL TO LOAD when its owner is empty. A compile that still
        # SUCCEEDS on a blanked owner (even with non-golden output) means the decision is sourced
        # elsewhere -- the owner is not load-bearing for it.
        print("NOT WIRED: blanking the herbert_owner did NOT break compilation -> not load-bearing -> RED.")
        return 1
    # CHECK-3 per-input structural differential (owner CONTENT drives per-statement verdict)
    if not _am_struct_differential(golden):
        print("NOT WIRED: structural differential failed -- owner content does not drive the "
              "do-statement shape (admissibility / call-count) per input -> RED.")
        return 1
    print("WIRED: 'array_mutation' -- keyword AND void-gating AND exactly-one-call are owner-driven "
          "(every structural poison bites), owner is load-bearing + array_mutation-specific, and "
          "content drives per-input -> GREEN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
