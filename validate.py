#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Validate the smell corpus and regenerate the catalog.

    uv run validate.py                  # check everything, exit 1 on any error
    uv run validate.py --write-catalog  # regenerate catalog.json from snippets/

Every check hard-blocks: for a data repository a soft warning is a warning nobody reads
and a schema that quietly fragments. See docs/002-snippet-design.md.
"""

from __future__ import annotations

import ast
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
SNIPPETS = ROOT / "snippets"
TAXONOMY = ROOT / "TAXONOMY.md"
CATALOG = ROOT / "catalog.json"

SCHEMA_VERSION = 1
MAX_SNIPPET_LINES = 15
SEVERITIES = ("bug", "trap", "taste")
SLUG_RE = re.compile(r"^[a-z0-9-]+$")

REQUIRED = (
    "language",
    "python",
    "severity",
    "category",
    "topic",
    "tags",
    "keywords",
    "signature",
    "distinguish",
    "added",
)
OPTIONAL = ("aliases", "source")
CATALOG_FIELDS = ("signature", "severity", "category", "topic", "tags", "keywords")
SECTIONS = ("Smell", "Why it's bad", "Better")

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
FENCE_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)


class Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, where: str, field: str | None, message: str) -> None:
        location = f"{where}:{field}" if field else where
        self.items.append(f"{location}: {message}")

    def report(self) -> int:
        for item in self.items:
            print(f"FAIL {item}", file=sys.stderr)
        return 1 if self.items else 0


def load_taxonomy() -> dict[str, set[str]]:
    """Values are the backticked identifiers listed under each H2 of TAXONOMY.md."""
    lists: dict[str, set[str]] = {}
    heading = None
    for line in TAXONOMY.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            heading = line[3:].strip().lower()
            lists.setdefault(heading, set())
        elif heading and (match := re.match(r"^- `([^`]+)`", line)):
            lists[heading].add(match.group(1))
    return lists


def split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = ""
        elif current is not None:
            sections[current] += line
    return sections


def section_order(body: str) -> list[str]:
    return [line[3:].strip() for line in body.splitlines() if line.startswith("## ")]


def is_one_sentence(text: str) -> bool:
    """One trailing period and no internal sentence break. Abbreviations will trip this."""
    stripped = text.strip()
    return stripped.endswith(".") and ". " not in stripped


def check_file(path: Path, taxonomy: dict[str, set[str]], errors: Errors) -> dict | None:
    where = str(path.relative_to(ROOT))
    slug = path.stem
    raw = path.read_text(encoding="utf-8")

    match = FRONTMATTER_RE.match(raw)
    if not match:
        errors.add(where, None, "no YAML frontmatter delimited by --- at the top of the file")
        return None

    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        errors.add(where, None, f"frontmatter is not valid YAML: {exc}")
        return None
    if not isinstance(meta, dict):
        errors.add(where, None, "frontmatter must be a mapping")
        return None

    if not SLUG_RE.match(slug):
        errors.add(where, None, "filename must match [a-z0-9-]+")

    for field in REQUIRED:
        if field not in meta:
            errors.add(where, field, "required field is missing")
        elif meta[field] is None or (isinstance(meta[field], str) and not meta[field].strip()):
            errors.add(where, field, "required field is empty")
    for field in meta:
        if field not in REQUIRED + OPTIONAL:
            errors.add(where, field, "unknown field")

    if (severity := meta.get("severity")) and severity not in SEVERITIES:
        errors.add(where, "severity", f"expected one of {', '.join(SEVERITIES)}, got {severity!r}")

    for field, heading in (("category", "category"), ("topic", "topic")):
        allowed = taxonomy.get(heading, set())
        value = meta.get(field)
        if value and value not in allowed:
            errors.add(where, field, f"{value!r} is not listed under ## {heading.title()} in TAXONOMY.md")

    if (language := meta.get("language")) and language != path.parent.name:
        errors.add(where, "language", f"{language!r} does not match directory {path.parent.name!r}")

    for field in ("tags", "keywords", "aliases"):
        if field in meta and not isinstance(meta[field], list):
            errors.add(where, field, "must be a list")

    for field in ("signature", "distinguish"):
        value = meta.get(field)
        if isinstance(value, str) and value.strip() and not is_one_sentence(value):
            errors.add(where, field, "must be exactly one sentence ending in a period")

    added = meta.get("added")
    if added is not None:
        if isinstance(added, dt.date):
            pass
        else:
            try:
                dt.date.fromisoformat(str(added))
            except ValueError:
                errors.add(where, "added", f"{added!r} is not an ISO 8601 date")

    body = match.group(2)
    headings = section_order(body)
    if headings != list(SECTIONS):
        errors.add(where, None, f"expected H2 sections {list(SECTIONS)} in order, got {headings}")
    if not re.search(r"^# \S", body, re.MULTILINE):
        errors.add(where, None, "body must open with an H1 title")

    sections = split_sections(body)
    for name in ("Smell", "Better"):
        blocks = FENCE_RE.findall(sections.get(name, ""))
        if len(blocks) != 1:
            errors.add(where, name, f"expected exactly one fenced code block, found {len(blocks)}")
            continue
        language_tag, code = blocks[0]
        if language_tag != "python":
            errors.add(where, name, f"code fence must be tagged python, got {language_tag!r}")
        lines = code.rstrip("\n").splitlines()
        if name == "Smell" and len(lines) > MAX_SNIPPET_LINES:
            errors.add(where, name, f"snippet is {len(lines)} lines, limit is {MAX_SNIPPET_LINES}")
        try:
            ast.parse(code)
        except SyntaxError as exc:
            errors.add(where, name, f"does not parse: {exc.msg} (line {exc.lineno})")

    if not sections.get("Why it's bad", "").strip():
        errors.add(where, "Why it's bad", "section is empty")

    entry = {"id": slug}
    entry.update({field: meta.get(field) for field in CATALOG_FIELDS})
    return {"entry": entry, "meta": meta, "path": path}


def check_identifiers(records: list[dict], errors: Errors) -> None:
    slugs = {record["entry"]["id"] for record in records}
    seen: dict[str, str] = {}
    for record in records:
        where = str(record["path"].relative_to(ROOT))
        for alias in record["meta"].get("aliases") or []:
            if alias in slugs:
                errors.add(where, "aliases", f"{alias!r} collides with an existing smell id")
            elif alias in seen:
                errors.add(where, "aliases", f"{alias!r} is already an alias of {seen[alias]!r}")
            else:
                seen[alias] = record["entry"]["id"]


def build_catalog(records: list[dict]) -> str:
    entries = sorted((record["entry"] for record in records), key=lambda entry: entry["id"])
    languages = {record["meta"].get("language") for record in records}
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "language": languages.pop() if len(languages) == 1 else sorted(filter(None, languages)),
        "count": len(entries),
        "smells": entries,
    }
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    write = "--write-catalog" in sys.argv[1:]
    errors = Errors()
    taxonomy = load_taxonomy()

    paths = sorted(SNIPPETS.glob("*/*.md"))
    if not paths:
        print(f"FAIL no smell files found under {SNIPPETS}", file=sys.stderr)
        return 1

    records = [record for path in paths if (record := check_file(path, taxonomy, errors))]
    check_identifiers(records, errors)

    catalog = build_catalog(records)
    if write:
        if errors.items:
            print("refusing to write catalog.json while validation fails", file=sys.stderr)
            return errors.report()
        CATALOG.write_text(catalog, encoding="utf-8")
        print(f"wrote {CATALOG.relative_to(ROOT)} ({len(records)} smells)")
        return 0

    if not CATALOG.exists():
        errors.add("catalog.json", None, "missing — run: uv run validate.py --write-catalog")
    elif CATALOG.read_text(encoding="utf-8") != catalog:
        errors.add(
            "catalog.json",
            None,
            "is stale relative to snippets/ — run: uv run validate.py --write-catalog",
        )

    status = errors.report()
    if not status:
        print(f"ok: {len(records)} smells, catalog fresh")
    return status


if __name__ == "__main__":
    sys.exit(main())
