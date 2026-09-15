#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Scaffold a new smell file from TEMPLATE.md.

    uv run new_smell.py                          # interactive: asks for everything
    uv run new_smell.py mutable-default-argument # asks only for the filing
    uv run new_smell.py my-smell --severity trap --category correctness --topic mutability

Filing is the boring half of adding a smell, and getting it wrong means a failed CI run
over a typo in a closed list. This asks for the closed-list fields, offers only values
TAXONOMY.md actually lists, refuses a slug that collides with an existing id or alias, and
leaves the three fields that need thought — signature, distinguish, keywords — to you.

The taxonomy, the severities and the slug rule are imported from validate.py rather than
restated here, so a value added to TAXONOMY.md shows up in the prompts with no edit to
this script. The body scaffold is read from TEMPLATE.md for the same reason: this script
knows how to fill a smell file in, not what one looks like.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

from validate import FRONTMATTER_RE, SEVERITIES, SLUG_RE, SNIPPETS, SNIPPET_LINES, load_taxonomy

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "TEMPLATE.md"
DEFAULT_LANGUAGE = "python"
H1_RE = re.compile(r"^# .+$", re.MULTILINE)

# Words too common to say anything about whether two slugs describe the same smell.
STOPWORDS = frozenset(
    {"a", "an", "the", "in", "on", "of", "as", "at", "to", "by", "for", "with", "and", "or", "is", "its"}
)


def existing_identifiers() -> dict[str, str]:
    """Every id and alias in the corpus, mapped to the file that claims it."""
    claimed: dict[str, str] = {}
    for path in sorted(SNIPPETS.glob("*/*/*.md")):
        where = str(path.relative_to(ROOT))
        claimed[path.stem] = where
        if match := FRONTMATTER_RE.match(path.read_text(encoding="utf-8")):
            meta = yaml.safe_load(match.group(1)) or {}
            if isinstance(meta, dict):
                for alias in meta.get("aliases") or []:
                    claimed[str(alias)] = where
    return claimed


def neighbours(slug: str, limit: int = 3) -> list[str]:
    """Existing ids sharing a word with the slug — the cheap version of "is this already here"."""
    words = {word for word in slug.split("-")} - STOPWORDS
    scored = []
    for path in sorted(SNIPPETS.glob("*/*/*.md")):
        if path.stem == slug:
            continue
        if overlap := len(words & (set(path.stem.split("-")) - STOPWORDS)):
            scored.append((overlap, path.stem))
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [stem for _, stem in scored[:limit]]


def default_source() -> str:
    """`source` is optional credit for the contributor, so the git identity is a fair guess."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, timeout=5, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ")
    return words[:1].upper() + words[1:]


def choose(prompt: str, options: list[str], default: str | None = None) -> str:
    """Numbered menu over a closed list. Only reached when stdin is a terminal."""
    print(f"\n{prompt}")
    for index, option in enumerate(options, start=1):
        marker = "  (default)" if option == default else ""
        print(f"  {index:>2}. {option}{marker}")
    while True:
        answer = input("> ").strip()
        if not answer and default:
            return default
        if answer in options:
            return answer
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print(f"pick 1-{len(options)}, or type the value")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    return input(f"\n{prompt}{suffix}\n> ").strip() or default


def resolve(
    name: str,
    value: str | None,
    options: list[str],
    interactive: bool,
    default: str | None = None,
    *,
    assume_default: bool = False,
) -> str:
    """The flag if given, a menu if we have a terminal, an error listing the choices otherwise.

    ``assume_default`` is for a field with a right answer nearly every time — `group`, and
    only `group`. The filing fields have no safe default: a wrong severity or topic files
    the smell where nobody looking for it will search, so a script with no terminal is
    told to say which it meant.
    """
    if value is not None:
        if value not in options:
            sys.exit(f"error: --{name}={value!r} is not one of: {', '.join(options)}")
        return value
    if not interactive:
        if assume_default and default:
            return default
        sys.exit(f"error: --{name} is required when not on a terminal; one of: {', '.join(options)}")
    return choose(f"{name}?", options, default)


def fill_template(template: str, values: dict[str, str], title: str) -> str:
    """Set the given frontmatter keys and the H1, and change nothing else in TEMPLATE.md.

    Line-wise substitution rather than a YAML round trip: the template's key order, its
    quoting and its placeholder prose are all things a contributor reads, and yaml.dump
    loses every one of them. A value of "" drops the key, which is how an optional field
    goes away.
    """
    match = FRONTMATTER_RE.match(template)
    if not match:
        sys.exit("error: TEMPLATE.md has no YAML frontmatter")

    lines = []
    seen = set()
    for line in match.group(1).splitlines():
        key = line.split(":", 1)[0]
        if key in values and key not in seen:
            seen.add(key)
            if values[key]:
                lines.append(f"{key}: {values[key]}")
        else:
            lines.append(line)
    if missing := set(values) - seen:
        sys.exit(f"error: TEMPLATE.md has no {', '.join(sorted(missing))} field to fill in")

    body, count = H1_RE.subn(f"# {title}", match.group(2), count=1)
    if not count:
        sys.exit("error: TEMPLATE.md body has no H1 title to replace")
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="new_smell.py", description="Scaffold a new smell file from TEMPLATE.md."
    )
    parser.add_argument("slug", nargs="?", help="filename of the smell, e.g. mutable-default-argument")
    parser.add_argument("--group", choices=sorted(SNIPPET_LINES), help="snippet size ceiling (default: code)")
    parser.add_argument("--severity", choices=SEVERITIES, help="bug, trap or taste")
    parser.add_argument("--category", help="a value listed under ## Category in TAXONOMY.md")
    parser.add_argument("--topic", help="a value listed under ## Topic in TAXONOMY.md")
    parser.add_argument("--title", help="H1 title (default: the slug, de-hyphenated)")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="corpus language (default: python)")
    parser.add_argument("--source", help="contributor credit (default: git config user.name)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing file")
    parser.add_argument("--edit", action="store_true", help="open the new file in $EDITOR")
    args = parser.parse_args()

    taxonomy = load_taxonomy()
    interactive = sys.stdin.isatty()

    slug = args.slug
    if slug is None:
        if not interactive:
            sys.exit("error: a slug is required when not on a terminal; see --help")
        slug = ask("slug? name it after the smell, not the fix")
    slug = slug.strip().removesuffix(".md")
    if not SLUG_RE.match(slug):
        sys.exit(f"error: slug {slug!r} must match [a-z0-9-]+")

    claimed = existing_identifiers()
    if slug in claimed:
        sys.exit(f"error: {slug!r} is already the id or an alias of {claimed[slug]}")
    if related := neighbours(slug):
        print(f"note: check these first, they share a word with your slug: {', '.join(related)}")

    group = resolve("group", args.group, sorted(SNIPPET_LINES), interactive, "code", assume_default=True)
    severity = resolve("severity", args.severity, list(SEVERITIES), interactive, default="trap")
    category = resolve("category", args.category, sorted(taxonomy.get("category", ())), interactive)
    topic = resolve("topic", args.topic, sorted(taxonomy.get("topic", ())), interactive)

    title = args.title or (ask("title?", title_from_slug(slug)) if interactive else title_from_slug(slug))
    source = args.source if args.source is not None else default_source()

    path = SNIPPETS / args.language / group / f"{slug}.md"
    if not path.parent.is_dir():
        sys.exit(f"error: {path.parent.relative_to(ROOT)} does not exist")
    if path.exists() and not args.force:
        sys.exit(f"error: {path.relative_to(ROOT)} already exists; pass --force to overwrite")

    values = {
        "language": args.language,
        "severity": severity,
        "category": category,
        "topic": topic,
        "added": dt.date.today().isoformat(),
        "source": source,
    }
    path.write_text(fill_template(TEMPLATE.read_text(encoding="utf-8"), values, title), encoding="utf-8")

    print(f"\nwrote {path.relative_to(ROOT)} — the ## Smell ceiling in {group}/ is {SNIPPET_LINES[group]} lines")
    print("next:")
    print("  1. write the snippet, ## Why it's bad, and ## Better")
    print("  2. write signature, distinguish and keywords — the three fields that need thought")
    print("  3. make catalog   # regenerate catalog.json")
    print("  4. make check     # what CI runs")

    if args.edit:
        if editor := os.environ.get("EDITOR") or os.environ.get("VISUAL"):
            return subprocess.call([*shlex.split(editor), str(path)])
        print("note: --edit needs $EDITOR or $VISUAL set", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
