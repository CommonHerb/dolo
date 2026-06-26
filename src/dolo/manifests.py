from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .compiler import compile_source
from .herbert_surface import HERBERT_BUILTIN_ARITIES
from .parser import parse_source
from .tokens import DoloSyntaxError


class ManifestError(ValueError):
    pass


ARRAY_MUTATION_CANDIDATE = "experiments/herbert/array_mutation_candidate.herb"
ARRAY_MUTATION_HERBERT_GOLDEN = "tests/fixtures/array_mutation.herb"
BUILTIN_ARITY_CANDIDATE = "experiments/herbert/builtin_arity_candidate.herb"
RECORD_FIELD_INDEX_CANDIDATE = "experiments/herbert/record_field_index_candidate.herb"
RECORD_FIELD_INDEX_EXAMPLE = "examples/citizen.dolo"
RECORD_FIELD_INDEX_RECORD = "Citizen"
ARRAY_RETURN_CALL_PATTERN = re.compile(r"\b(?:count|get|freeze)\([^)]*\)")


def read_manifest_rows(path: Path, *, columns: int) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line or line.startswith("#"):
            continue
        fields = tuple(line.split("\t"))
        if len(fields) != columns:
            raise ManifestError(
                f"{path.name}:{line_number}: expected {columns} "
                f"tab-separated fields, got {len(fields)}"
            )
        for field in fields:
            if not field:
                raise ManifestError(f"{path.name}:{line_number}: empty manifest field")
        rows.append(fields)
    return rows


def validate_repository_manifests(root: Path) -> None:
    fixtures = root / "tests" / "fixtures"
    executable_rows = _read_sorted(fixtures / "executable_manifest.tsv", columns=3)
    migration_rows = _read_sorted(
        fixtures / "herbert_migration_manifest.tsv",
        columns=2,
    )
    non_executable_rows = _read_sorted(
        fixtures / "non_executable_examples.tsv",
        columns=2,
    )
    _reject_duplicate_sources(
        executable_rows,
        manifest_name="executable_manifest.tsv",
    )
    _reject_duplicate_sources(
        migration_rows,
        manifest_name="herbert_migration_manifest.tsv",
    )
    _reject_duplicate_sources(
        non_executable_rows,
        manifest_name="non_executable_examples.tsv",
    )
    _reject_duplicate_field(
        executable_rows,
        field_index=1,
        manifest_name="executable_manifest.tsv",
        label="Herbert golden",
    )
    _reject_duplicate_field(
        executable_rows,
        field_index=2,
        manifest_name="executable_manifest.tsv",
        label="stdout golden",
    )
    _reject_duplicate_field(
        migration_rows,
        field_index=1,
        manifest_name="herbert_migration_manifest.tsv",
        label="stdout golden",
    )

    if not executable_rows:
        raise ManifestError(
            "executable_manifest.tsv: expected at least one executable example"
        )
    if not migration_rows:
        raise ManifestError(
            "herbert_migration_manifest.tsv: expected at least one migration candidate"
        )

    executable_sources = set()
    for source_rel, herb_rel, stdout_rel in executable_rows:
        _require_file(root, source_rel, label="source")
        _require_example_source(
            source_rel,
            manifest_name="executable_manifest.tsv",
        )
        _require_no_arg_main(root, source_rel)
        _require_file(root, herb_rel, label="Herbert golden")
        _require_suffix(
            herb_rel,
            suffix=".herb",
            manifest_name="executable_manifest.tsv",
            label="Herbert golden",
        )
        _require_parent(
            herb_rel,
            parent=Path("tests") / "fixtures",
            manifest_name="executable_manifest.tsv",
            label="Herbert golden",
        )
        _require_herbert_golden_matches(root, source_rel, herb_rel)
        _require_file(root, stdout_rel, label="stdout golden")
        _require_suffix(
            stdout_rel,
            suffix=".stdout",
            manifest_name="executable_manifest.tsv",
            label="stdout golden",
        )
        _require_parent(
            stdout_rel,
            parent=Path("tests") / "fixtures",
            manifest_name="executable_manifest.tsv",
            label="stdout golden",
        )
        _require_stdout_newline(
            root,
            stdout_rel,
            manifest_name="executable_manifest.tsv",
        )
        executable_sources.add(source_rel)

    for source_rel, stdout_rel in migration_rows:
        _require_file(root, source_rel, label="migration source")
        _require_migration_main(root, source_rel)
        _require_file(root, stdout_rel, label="migration stdout golden")
        _require_suffix(
            stdout_rel,
            suffix=".stdout",
            manifest_name="herbert_migration_manifest.tsv",
            label="stdout golden",
        )
        _require_parent(
            stdout_rel,
            parent=Path("tests") / "fixtures",
            manifest_name="herbert_migration_manifest.tsv",
            label="stdout golden",
        )
        _require_stdout_newline(
            root,
            stdout_rel,
            manifest_name="herbert_migration_manifest.tsv",
        )
        _require_migration_candidate_note(root, source_rel, stdout_rel)
        _require_array_mutation_candidate_matches_emitted_fixture(root, source_rel)
        _require_builtin_arity_candidate_matches_python_table(root, source_rel)
        _require_record_field_index_candidate_matches_dolo_record(root, source_rel)
    _require_migration_candidate_notes_are_manifested(
        root,
        {source_rel for source_rel, _ in migration_rows},
    )

    non_executable_sources = set()
    for source_rel, reason in non_executable_rows:
        _require_file(root, source_rel, label="source")
        _require_example_source(
            source_rel,
            manifest_name="non_executable_examples.tsv",
        )
        if not reason.strip():
            raise ManifestError(
                f"non_executable_examples.tsv: missing reason for {source_rel}"
            )
        non_executable_sources.add(source_rel)

    overlap = executable_sources & non_executable_sources
    if overlap:
        source = sorted(overlap)[0]
        raise ManifestError(
            f"example cannot be both executable and non-executable: {source}"
        )

    examples = {
        str(path.relative_to(root))
        for path in sorted((root / "examples").glob("*.dolo"))
    }
    classified = executable_sources | non_executable_sources
    missing = examples - classified
    if missing:
        source = sorted(missing)[0]
        raise ManifestError(f"example is not classified for execution: {source}")


def _read_sorted(path: Path, *, columns: int) -> list[tuple[str, ...]]:
    if not path.is_file():
        raise ManifestError(f"{path.name}: manifest is required")
    rows = read_manifest_rows(path, columns=columns)
    if rows != sorted(rows):
        raise ManifestError(f"{path.name}: rows must be sorted")
    return rows


def _reject_duplicate_sources(
    rows: list[tuple[str, ...]],
    *,
    manifest_name: str,
) -> None:
    seen: set[str] = set()
    for row in rows:
        source = row[0]
        if source in seen:
            raise ManifestError(f"{manifest_name}: duplicate source {source}")
        seen.add(source)


def _reject_duplicate_field(
    rows: list[tuple[str, ...]],
    *,
    field_index: int,
    manifest_name: str,
    label: str,
) -> None:
    seen: set[str] = set()
    for row in rows:
        value = row[field_index]
        if value in seen:
            raise ManifestError(f"{manifest_name}: duplicate {label} {value}")
        seen.add(value)


def _require_suffix(
    relative_path: str,
    *,
    suffix: str,
    manifest_name: str,
    label: str,
) -> None:
    if Path(relative_path).suffix != suffix:
        raise ManifestError(
            f"{manifest_name}: {label} must be {suffix}: {relative_path}"
        )


def _require_example_source(relative_path: str, *, manifest_name: str) -> None:
    _require_suffix(
        relative_path,
        suffix=".dolo",
        manifest_name=manifest_name,
        label="source",
    )
    _require_parent(
        relative_path,
        parent=Path("examples"),
        manifest_name=manifest_name,
        label="source",
    )


def _require_parent(
    relative_path: str,
    *,
    parent: Path,
    manifest_name: str,
    label: str,
) -> None:
    if Path(relative_path).parent != parent:
        raise ManifestError(
            f"{manifest_name}: {label} must live under {parent}/: {relative_path}"
        )


def _require_stdout_newline(
    root: Path,
    relative_path: str,
    *,
    manifest_name: str,
) -> None:
    if not (root / relative_path).read_bytes().endswith(b"\n"):
        raise ManifestError(
            f"{manifest_name}: stdout golden must end with newline: {relative_path}"
        )


def _require_herbert_golden_matches(
    root: Path,
    source_rel: str,
    herb_rel: str,
) -> None:
    generated = compile_source((root / source_rel).read_text())
    expected = (root / herb_rel).read_text()
    if generated != expected:
        raise ManifestError(
            "executable_manifest.tsv: generated Herbert does not match golden: "
            f"{source_rel} -> {herb_rel}"
        )


def _require_no_arg_main(root: Path, source_rel: str) -> None:
    source_path = root / source_rel
    try:
        program = parse_source(source_path.read_text())
    except DoloSyntaxError as exc:
        raise ManifestError(
            f"executable_manifest.tsv: {source_rel} failed to parse: {exc}"
        ) from exc
    for function in program.functions:
        if function.name == "main" and not function.params:
            return
    raise ManifestError(
        f"executable_manifest.tsv: {source_rel} must define no-argument fn main()"
    )


def _require_migration_main(root: Path, source_rel: str) -> None:
    source_path = root / source_rel
    if source_path.suffix != ".herb":
        raise ManifestError(
            f"herbert_migration_manifest.tsv: migration source must be .herb: {source_rel}"
        )
    _require_parent(
        source_rel,
        parent=Path("experiments") / "herbert",
        manifest_name="herbert_migration_manifest.tsv",
        label="migration source",
    )
    if "func main()" not in source_path.read_text():
        raise ManifestError(
            f"herbert_migration_manifest.tsv: {source_rel} must define func main()"
        )


def _require_migration_candidate_note(
    root: Path,
    source_rel: str,
    stdout_rel: str,
) -> None:
    docs_dir = root / "docs"
    if not docs_dir.exists():
        return
    notes_dir = docs_dir / "migration-candidates"
    if not notes_dir.is_dir():
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate notes must live under "
            "docs/migration-candidates/"
        )
    source_notes: list[Path] = []
    stdout_notes: list[Path] = []
    for note in sorted(notes_dir.glob("*.md")):
        text = note.read_text()
        if source_rel in text:
            source_notes.append(note)
            if stdout_rel in text:
                stdout_notes.append(note)
    if not source_notes:
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate note must mention "
            f"{source_rel}"
        )
    if not stdout_notes:
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate note must mention "
            f"{stdout_rel}"
        )
    if not any(_names_python_owner(note.read_text()) for note in stdout_notes):
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate note must name "
            f"the current Python/bootstrap owner for {source_rel}"
        )
    if not any(_names_replacement_path(note.read_text()) for note in stdout_notes):
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate note must include "
            f"a replacement path for {source_rel}"
        )
    if not any(_states_authority_boundary(note.read_text()) for note in stdout_notes):
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate note must state "
            f"the authority boundary for {source_rel}"
        )


def _require_migration_candidate_notes_are_manifested(
    root: Path,
    migration_sources: set[str],
) -> None:
    docs_dir = root / "docs"
    if not docs_dir.exists():
        return
    notes_dir = docs_dir / "migration-candidates"
    if not notes_dir.is_dir():
        raise ManifestError(
            "herbert_migration_manifest.tsv: migration candidate notes must live under "
            "docs/migration-candidates/"
        )
    for note in sorted(notes_dir.glob("*.md")):
        text = note.read_text()
        if not any(source in text for source in migration_sources):
            note_rel = note.relative_to(root)
            raise ManifestError(
                "herbert_migration_manifest.tsv: migration candidate note "
                f"is not linked to a manifest source: {note_rel}"
            )


def _require_builtin_arity_candidate_matches_python_table(
    root: Path,
    source_rel: str,
) -> None:
    if source_rel != BUILTIN_ARITY_CANDIDATE:
        return

    actual = _extract_builtin_arity_candidate_map((root / source_rel).read_text())
    expected = dict(sorted(HERBERT_BUILTIN_ARITIES.items()))
    if actual == expected:
        return

    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    mismatched = sorted(
        name
        for name in set(expected) & set(actual)
        if expected[name] != actual[name]
    )
    details: list[str] = []
    if missing:
        details.append(f"missing {', '.join(missing)}")
    if unexpected:
        details.append(f"unexpected {', '.join(unexpected)}")
    if mismatched:
        details.append(
            "mismatched "
            + ", ".join(
                f"{name} expected {expected[name]} got {actual[name]}"
                for name in mismatched
            )
        )
    raise ManifestError(
        "herbert_migration_manifest.tsv: builtin arity candidate must mirror "
        "HERBERT_BUILTIN_ARITIES "
        f"({'; '.join(details)})"
    )


def _require_array_mutation_candidate_matches_emitted_fixture(
    root: Path,
    source_rel: str,
) -> None:
    if source_rel != ARRAY_MUTATION_CANDIDATE:
        return

    golden_path = root / ARRAY_MUTATION_HERBERT_GOLDEN
    if not golden_path.is_file():
        raise ManifestError(
            "herbert_migration_manifest.tsv: array mutation comparison fixture "
            f"missing: {ARRAY_MUTATION_HERBERT_GOLDEN}"
        )

    expected = _extract_array_mutation_shape(golden_path.read_text())
    actual = _extract_array_mutation_shape((root / source_rel).read_text())
    if actual == expected:
        return

    missing = [item for item in expected if item not in actual]
    unexpected = [item for item in actual if item not in expected]
    details: list[str] = []
    if missing:
        details.append(f"missing {', '.join(missing)}")
    if unexpected:
        details.append(f"unexpected {', '.join(unexpected)}")
    if not details:
        details.append("sequence differed")
    raise ManifestError(
        "herbert_migration_manifest.tsv: array mutation candidate must mirror "
        f"{ARRAY_MUTATION_HERBERT_GOLDEN} ({'; '.join(details)})"
    )


def _extract_array_mutation_shape(text: str) -> list[str]:
    shape: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("let ")
            and ("= new_array(" in stripped or "= new_buffer()" in stripped)
        ):
            shape.append(stripped)
        elif stripped.startswith("do add(") or stripped.startswith("do append("):
            shape.append(stripped)
        elif stripped.startswith("return "):
            calls = ARRAY_RETURN_CALL_PATTERN.findall(stripped)
            if calls:
                shape.append("return " + ", ".join(calls))
    return shape


def _extract_builtin_arity_candidate_map(text: str) -> dict[str, int]:
    return _extract_equal_return_map(text)


def _require_record_field_index_candidate_matches_dolo_record(
    root: Path,
    source_rel: str,
) -> None:
    if source_rel != RECORD_FIELD_INDEX_CANDIDATE:
        return

    example_path = root / RECORD_FIELD_INDEX_EXAMPLE
    if not example_path.is_file():
        raise ManifestError(
            "herbert_migration_manifest.tsv: record field index comparison source "
            f"missing: {RECORD_FIELD_INDEX_EXAMPLE}"
        )
    try:
        program = parse_source(example_path.read_text())
    except DoloSyntaxError as exc:
        raise ManifestError(
            "herbert_migration_manifest.tsv: record field index comparison source "
            f"failed to parse: {exc}"
        ) from exc

    record = next(
        (
            candidate
            for candidate in program.records
            if candidate.name == RECORD_FIELD_INDEX_RECORD
        ),
        None,
    )
    if record is None:
        raise ManifestError(
            "herbert_migration_manifest.tsv: record field index comparison source "
            f"must define record {RECORD_FIELD_INDEX_RECORD}"
        )

    actual = _extract_equal_return_map((root / source_rel).read_text())
    expected = {field: index for index, field in enumerate(record.fields)}
    if actual == expected:
        return

    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    mismatched = sorted(
        field
        for field in set(expected) & set(actual)
        if expected[field] != actual[field]
    )
    details: list[str] = []
    if missing:
        details.append(f"missing {', '.join(missing)}")
    if unexpected:
        details.append(f"unexpected {', '.join(unexpected)}")
    if mismatched:
        details.append(
            "mismatched "
            + ", ".join(
                f"{field} expected {expected[field]} got {actual[field]}"
                for field in mismatched
            )
        )
    raise ManifestError(
        "herbert_migration_manifest.tsv: record field index candidate must mirror "
        f"{RECORD_FIELD_INDEX_EXAMPLE} {RECORD_FIELD_INDEX_RECORD} fields "
        f"({'; '.join(details)})"
    )


def _extract_equal_return_map(text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    lines = text.splitlines()
    prefix = 'if equal(name, "'
    suffix = '"):'
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if not stripped.startswith(prefix) or not stripped.endswith(suffix):
            continue
        name = stripped[len(prefix) : -len(suffix)]
        return_line = lines[index + 1].strip()
        if not return_line.startswith("return "):
            continue
        arity_text = return_line.removeprefix("return ").strip()
        if arity_text.isdigit():
            found[name] = int(arity_text)
    return dict(sorted(found.items()))


def _names_python_owner(text: str) -> bool:
    owner_phrases = (
        "Current Python behavior lives",
        "Python behavior lives",
        "Current bootstrap behavior lives",
        "Bootstrap behavior lives",
        "Current Python-owned",
        "Python-owned",
    )
    return any(phrase in text for phrase in owner_phrases)


def _names_replacement_path(text: str) -> bool:
    return "## Replacement Path" in text or "## Wiring Path" in text


def _states_authority_boundary(text: str) -> bool:
    authority_phrases = (
        "not compiler authority",
        "not Dolo's compiler authority",
        "not semantic authority",
        "not Dolo's semantic authority",
        "not paid debt",
    )
    return "## Authority Boundary" in text and any(
        phrase in text for phrase in authority_phrases
    )


def _require_file(root: Path, relative_path: str, *, label: str) -> None:
    _require_repository_relative_path(relative_path, label=label)
    if not (root / relative_path).is_file():
        raise ManifestError(f"{label} missing: {relative_path}")


def _require_repository_relative_path(relative_path: str, *, label: str) -> None:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ManifestError(f"{label} must be repository-relative: {relative_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dolo.manifests")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("command", choices=("verify",))
    args = parser.parse_args(argv)

    try:
        validate_repository_manifests(args.root)
    except ManifestError as exc:
        print(f"dolo manifests: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
