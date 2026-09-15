"""Reading layer over the corpus.

Catalog entries come from the committed ``catalog.json`` (see docs/adr/007). Full records
are parsed from the markdown on demand, because they are only ever needed for the handful
of smells a caller shortlisted.

The frontmatter parsing here is deliberately duplicated from the repository's
``validate.py``: contributors must be able to validate a snippet without installing this
server. The schema those two agree on is documented in docs/002-snippet-design.md.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from packaging.specifiers import InvalidSpecifier, SpecifierSet

SCHEMA_VERSION = 1

#: Where the wheel keeps its copy of the corpus, relative to this module.
BUNDLED_DIRNAME = "_corpus"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
FENCE_RE = re.compile(r"```\w*\n(.*?)```", re.DOTALL)
H1_RE = re.compile(r"^# (.+)$", re.MULTILINE)

RECORD_FIELDS = (
    "signature",
    "distinguish",
    "severity",
    "category",
    "topic",
    "tags",
    "keywords",
    "language",
    "python",
    "added",
    "source",
)


class CorpusError(RuntimeError):
    """The corpus on disk is missing or unreadable."""


def _is_root(path: Path) -> bool:
    return (path / "catalog.json").is_file() and (path / "snippets").is_dir()


def _bundled_root(base: Path | None = None) -> Path | None:
    """The corpus copy shipped inside the wheel, or None when running from a checkout.

    ``uv tool install`` drops the package into a venv with no corpus anywhere above it, so
    an installed server reads the copy force-included beside this module (see pyproject).
    """
    root = (base or Path(__file__).resolve().parent) / BUNDLED_DIRNAME
    return root if _is_root(root) else None


def find_root(start: Path | None = None) -> Path:
    """Locate the corpus root, i.e. the directory holding catalog.json and snippets/.

    Resolution order: ``ART_BIN_ROOT``, then the checkout this module lives in, then the
    copy bundled into the wheel. The checkout wins over the bundle so a contributor
    running from a clone always reads their own edits; the bundle is what makes an
    installed tool work at all. ``ART_BIN_ROOT`` overrides both, which is what a
    deployment that separates the server from the corpus would set.
    """
    if override := os.environ.get("ART_BIN_ROOT"):
        root = Path(override).expanduser().resolve()
        if not (root / "snippets").is_dir():
            raise CorpusError(f"ART_BIN_ROOT={root} does not contain a snippets/ directory")
        return root

    for candidate in (start or Path(__file__).resolve()).parents:
        if _is_root(candidate):
            return candidate

    if bundled := _bundled_root():
        return bundled

    raise CorpusError(
        "could not locate the corpus: no parent directory contains both catalog.json and "
        "snippets/, and this install ships no bundled copy. Set ART_BIN_ROOT to the "
        "repository root."
    )


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise CorpusError(f"{path}: no YAML frontmatter")
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        raise CorpusError(f"{path}: frontmatter is not a mapping")
    return meta, match.group(2)


def _sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = ""
        elif current is not None:
            sections[current] += line
    return sections


def _code(section: str) -> str:
    match = FENCE_RE.search(section)
    return match.group(1).rstrip("\n") if match else ""


def _bullets(section: str) -> list[str]:
    """Collect ``- `` bullets, folding wrapped continuation lines back onto one line."""
    bullets: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
        elif stripped and bullets and line.startswith((" ", "\t")):
            bullets[-1] += " " + stripped
    return bullets


def parse_record(path: Path) -> dict[str, Any]:
    """Parse one smell file into a full record, as returned by ``get_smells``."""
    meta, body = _split_frontmatter(path.read_text(encoding="utf-8"), path)
    sections = _sections(body)
    title = match.group(1).strip() if (match := H1_RE.search(body)) else path.stem

    record: dict[str, Any] = {"id": path.stem, "resolved_from": None}
    for field in RECORD_FIELDS:
        value = meta.get(field)
        record[field] = str(value) if field == "added" and value is not None else value
    record["title"] = title
    record["snippet"] = _code(sections.get("Smell", ""))
    record["why_bad"] = _bullets(sections.get("Why it's bad", ""))
    record["better"] = _code(sections.get("Better", ""))
    return record


def _matches_version(spec: str | None, version: str) -> bool:
    """True when ``version`` satisfies a smell's ``python`` range. Unparseable ranges match."""
    if not spec:
        return True
    try:
        return SpecifierSet(spec).contains(version, prereleases=True)
    except InvalidSpecifier:
        return True


@dataclass
class Corpus:
    """Read-only view of the corpus. Records are cached per file and invalidated by mtime."""

    root: Path

    def __post_init__(self) -> None:
        self._records: dict[str, tuple[float, dict[str, Any]]] = {}
        self._aliases: dict[str, str] | None = None

    @classmethod
    def discover(cls) -> Corpus:
        return cls(find_root())

    @property
    def catalog_path(self) -> Path:
        return self.root / "catalog.json"

    def _snippet_paths(self) -> list[Path]:
        return sorted((self.root / "snippets").glob("*/*/*.md"))

    def _path_for(self, slug: str) -> Path | None:
        """Resolve a slug to a file without trusting it as a path component."""
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            return None
        for path in self._snippet_paths():
            if path.stem == slug:
                return path
        return None

    def catalog(self) -> dict[str, Any]:
        try:
            return json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise CorpusError(
                f"{self.catalog_path} is missing — run: uv run validate.py --write-catalog"
            ) from exc
        except json.JSONDecodeError as exc:
            raise CorpusError(f"{self.catalog_path} is not valid JSON: {exc}") from exc

    def record(self, slug: str) -> dict[str, Any] | None:
        path = self._path_for(slug)
        if path is None:
            return None
        mtime = path.stat().st_mtime
        cached = self._records.get(slug)
        if cached is None or cached[0] != mtime:
            self._records[slug] = (mtime, parse_record(path))
        return dict(self._records[slug][1])

    def alias_index(self) -> dict[str, str]:
        """Map alias -> canonical slug. Built on first miss, since aliases are not in the catalog."""
        if self._aliases is None:
            index: dict[str, str] = {}
            for path in self._snippet_paths():
                meta, _ = _split_frontmatter(path.read_text(encoding="utf-8"), path)
                for alias in meta.get("aliases") or []:
                    index.setdefault(str(alias), path.stem)
            self._aliases = index
        return self._aliases

    def list_smells(
        self,
        severity: list[str] | None = None,
        category: list[str] | None = None,
        topic: list[str] | None = None,
        language: str = "python",
        python_version: str | None = None,
    ) -> dict[str, Any]:
        catalog = self.catalog()
        smells = catalog.get("smells", [])
        languages = catalog.get("language")
        languages = [languages] if isinstance(languages, str) else list(languages or [])
        if language and languages and language not in languages:
            smells = []

        wanted = {"severity": severity, "category": category, "topic": topic}
        for field, values in wanted.items():
            if values:
                allowed = set(values)
                smells = [smell for smell in smells if smell.get(field) in allowed]

        if python_version:
            keep = []
            for smell in smells:
                record = self.record(smell["id"])
                if _matches_version(record.get("python") if record else None, python_version):
                    keep.append(smell)
            smells = keep

        return {
            "schema_version": catalog.get("schema_version", SCHEMA_VERSION),
            "language": catalog.get("language"),
            "count": len(smells),
            "smells": smells,
        }

    def get_smells(self, ids: list[str]) -> dict[str, Any]:
        records: list[dict[str, Any]] = []
        unknown: list[str] = []
        seen: set[str] = set()

        for requested in ids:
            slug = str(requested).strip()
            record = self.record(slug)
            resolved_from = None
            if record is None:
                if canonical := self.alias_index().get(slug):
                    record = self.record(canonical)
                    resolved_from = slug
            if record is None:
                unknown.append(slug)
                continue
            if record["id"] in seen:
                continue
            seen.add(record["id"])
            record["resolved_from"] = resolved_from
            records.append(record)

        return {"schema_version": SCHEMA_VERSION, "smells": records, "unknown": unknown}

    def taxonomy(self) -> dict[str, Any]:
        catalog = self.catalog()
        counts: dict[str, dict[str, int]] = {"category": {}, "topic": {}, "severity": {}}
        for smell in catalog.get("smells", []):
            for field in counts:
                if value := smell.get(field):
                    counts[field][value] = counts[field].get(value, 0) + 1
        return {
            "schema_version": catalog.get("schema_version", SCHEMA_VERSION),
            **{field: dict(sorted(values.items())) for field, values in counts.items()},
        }
