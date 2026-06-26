from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parser import parse_source
from .tokens import DoloSyntaxError


class ManifestError(ValueError):
    pass


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
        _require_no_arg_main(root, source_rel)
        _require_file(root, herb_rel, label="Herbert golden")
        _require_file(root, stdout_rel, label="stdout golden")
        executable_sources.add(source_rel)

    for source_rel, stdout_rel in migration_rows:
        _require_file(root, source_rel, label="migration source")
        _require_file(root, stdout_rel, label="migration stdout golden")

    non_executable_sources = set()
    for source_rel, reason in non_executable_rows:
        _require_file(root, source_rel, label="source")
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


def _require_file(root: Path, relative_path: str, *, label: str) -> None:
    if not (root / relative_path).is_file():
        raise ManifestError(f"{label} missing: {relative_path}")


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
