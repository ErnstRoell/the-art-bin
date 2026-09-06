---
title: Snippet Design
description: The anatomy of a smell file — frontmatter fields, body sections, taxonomy, and enforced constraints.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [schema, corpus, frontmatter, validation]
category: reference
related:
  - docs/001-system-overview.md
  - docs/003-mcp-api-overview.md
  - CONTEXT.md
---

# Snippet Design

One file is one smell. This document specifies exactly what that file contains, which parts are required, and
what the validator enforces. Every field exists to serve either the catalog (shortlisting) or the full record
(confirmation) — see [System Overview](./001-system-overview.md) for the two-phase flow those two roles come
from.

## File Location And Identity

Files live at `snippets/<language>/<slug>.md`. Today that is only `snippets/python/`.

**The filename is the identifier.** There is no `id` field; duplicating the slug into frontmatter would only
create something to drift. A slug is lowercase, hyphen-separated, and matches `[a-z0-9-]+`.

Name the slug after the smell, not after the fix: `mutable-default-argument`, not `use-none-default`. Renames
are a `git mv` plus an entry in `aliases`, which keeps previously cited identifiers resolvable
([ADR 008](./adr/008-filename-as-identifier-with-aliases.md)).

## Anatomy

```markdown
---
aliases: [mutable-default-arg]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [defaults, functions]
keywords: ["=[]", "={}", "def", "default argument", "append"]
signature: "A function default is a list or dict, so one object is shared across every call."
distinguish: "Fine when the default is immutable, or when shared state is the documented intent."
added: 2026-09-04
source: ernst
---

# Mutable default argument

## Smell

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket
```

## Why it's bad

- The list is created once, at definition time, and outlives the call.
- Callers who omit `basket` silently share state with every previous caller.
- The bug surfaces as data from an unrelated request appearing in this one, which is hard to trace back here.

## Better

```python
def add_item(item, basket=None):
    basket = [] if basket is None else basket
    basket.append(item)
    return basket
```
```

## Frontmatter Fields

| Field | Required | In catalog | Purpose |
| --- | --- | --- | --- |
| `signature` | yes | yes | One sentence naming the mechanism. The primary shortlisting field. |
| `severity` | yes | yes | `bug`, `trap`, or `taste`. What the smell actually costs. |
| `category` | yes | yes | Consequence axis. One value from the closed list. |
| `topic` | yes | yes | Python-feature axis. One value from the closed list. |
| `tags` | yes | yes | Open-ended conceptual labels. May be empty. |
| `keywords` | yes | yes | Lexical hooks — tokens likely to appear in offending code. |
| `language` | yes | no | `python`. Redundant with the path, but makes a file self-describing. |
| `python` | yes | no | Version range in which this is a smell, e.g. `">=3.0"`, `">=3.9"`, `"<3.12"`. |
| `distinguish` | yes | no | One sentence describing the near miss that is *not* this smell. |
| `added` | yes | no | ISO date the smell entered the corpus. |
| `aliases` | no | no | Previously used slugs, so old identifiers still resolve. |
| `source` | no | no | Optional credit for the contributor. Not a code provenance field. |

### Signature

The field the LLM shortlists on, so it is written to be matched rather than read aloud. One sentence, naming the
*mechanism* rather than the consequence. "A function default is a list or dict, so one object is shared across
every call" is a signature; "leads to confusing bugs" is not.

### Keywords Versus Tags

These look similar and are not.

- **`keywords`** are lexical: literal tokens, operators, and phrases likely to appear in or near the offending
  code — `"=[]"`, `"except:"`, `"global"`, `"eval"`. They exist so a shortlisting pass can hook onto surface
  text, and they are the field a future keyword search would index.
- **`tags`** are conceptual: open-ended labels for whatever `category` and `topic` do not capture — `defaults`,
  `legacy`, `django`. They exist for grouping and browsing.

A keyword that never appears in real code is useless; a tag that is just a restatement of the topic is noise.

### Distinguish

The most valuable field in the schema, and the one nothing else provides. Because the LLM does the matching, its
main failure mode is flagging correct code that merely resembles a smell. `distinguish` is the guard: it names
the legitimate variant explicitly.

A contributor who cannot write the near miss has not yet understood their own smell well enough to add it
([ADR 005](./adr/005-require-distinguish-and-better.md)).

### Severity

| Value | Meaning |
| --- | --- |
| `bug` | Wrong today. Produces incorrect behaviour as written. |
| `trap` | Works today, bites later. Correct until a condition changes, then fails surprisingly. |
| `taste` | Works and keeps working, but reads badly. |

`taste` is a first-class value, not a leftover bin — it is most of the reason the corpus exists
([ADR 004](./adr/004-severity-includes-taste.md)).

## Body Sections

Exactly three H2 sections, in this order, under an H1 with the smell's human-readable name.

1. **`## Smell`** — one fenced `python` block: the smallest code that demonstrates the problem.
2. **`## Why it's bad`** — bullets. The reasoning `signature` had no room for. Explain the mechanism and how the
   failure actually presents itself, since that is what makes it recognisable in the wild.
3. **`## Better`** — one fenced `python` block: what to write instead.

`## Better` is required for every smell regardless of severity. For a `bug` it is close to self-evident; for a
`taste` entry it is the entire payload, because "I dislike this" is unactionable without "write this instead."
Requiring it uniformly keeps the template simple and stops taste entries decaying into complaints.

## Taxonomy

Both lists are closed. Values live in `TAXONOMY.md`, and adding one is a deliberate pull request that edits that
file — not something a contributor does in passing ([ADR 003](./adr/003-two-axis-taxonomy.md)).

**`category`** — what the smell costs you:

`correctness`, `security`, `performance`, `readability`, `maintainability`, `testability`

**`topic`** — the Python feature it lives in:

`exceptions`, `mutability`, `typing`, `naming`, `functions`, `classes`, `control-flow`, `imports`, `strings`,
`io`, `concurrency`, `numerics`, `stdlib-misuse`

Three notes on maintaining these:

- `numerics` covers the array-programming stack rather than a language feature, because shape and dtype
  arithmetic is where a large share of scientific Python goes wrong and no other topic describes it.
- `stdlib-misuse` is a deliberate escape hatch, so contributors are not forced into a bad fit. If it grows past
  roughly 15% of the corpus, split it.
- There is no `style` category. That axis is what `severity: taste` carries; having both invites the same smell
  being filed two contradictory ways.

## Constraints

### Snippet Size

**The `## Smell` block is at most 15 lines, enforced.** This serves three goals at once: signal-to-noise, since
scaffolding dilutes the thing being illustrated; scope, since anything longer is an architectural pattern that
does not fit this schema; and non-recognisability, since no real code is ever that small, so the ceiling forces
reconstruction rather than pasting ([ADR 009](./adr/009-reconstructed-snippets-and-licensing.md)).

Longer smells and architecture-level anti-patterns are explicitly out of scope for now.

### Parseability

Both code blocks must satisfy `ast.parse`. They need not run, and need not be importable — plenty of smells
concern API shape or naming and have no meaningful runtime. Requiring *runnable* code would push contributors to
pad snippets with scaffolding, which fights the size ceiling. Requiring *parseable* code costs a one-line check
and keeps the corpus mechanically processable.

Ellipsis placeholders are fine, since `...` is valid Python:

```python
def handler(request, cache={}):
    ...
```

### One Smell Per Snippet

A snippet demonstrating three problems cannot carry one `signature`, one `category`, or one `distinguish`. Split
it. If the smells genuinely only occur together, that combination is itself the smell and needs its own name.

## Validation

`validate.py` runs in CI on every pull request. All checks hard-block: for a data repository, a soft warning is
a warning nobody reads and a schema that quietly fragments. The cost of hard-blocking is paid in error message
quality, so every failure reports the file, the field, and what was expected.

| Check | Rule |
| --- | --- |
| Required fields | Every required field is present and non-empty |
| Taxonomy | `category` and `topic` appear in `TAXONOMY.md` |
| Severity | `severity` is one of `bug`, `trap`, `taste` |
| Snippet size | The `## Smell` block is 15 lines or fewer |
| Parseability | Both code blocks pass `ast.parse` |
| Sentences | `signature` and `distinguish` are each a single sentence |
| Slug | Filename matches `[a-z0-9-]+` and equals no other file's slug |
| Aliases | No alias collides with any slug or any other alias in the corpus |
| Date | `added` is a valid ISO 8601 date |
| Body | Exactly the three required H2 sections, in order |
| Catalog freshness | `catalog.json` matches what regeneration would produce |

The alias-collision and catalog-freshness checks are the two that look like overhead now and are not: the first
protects identifiers that appear in review comments, the second contains the one real risk of committing a
generated file ([ADR 007](./adr/007-committed-generated-catalog.md)).

## Related Documents

- [System Overview](./001-system-overview.md) — where these fields are consumed
- [MCP API Overview](./003-mcp-api-overview.md) — how records reach the caller
- [CONTEXT.md](../CONTEXT.md) — definitions of smell, severity, category, topic, and the rest
