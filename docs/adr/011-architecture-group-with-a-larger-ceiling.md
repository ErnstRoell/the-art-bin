---
title: Architecture Group With A Larger Ceiling
description: A group directory below the language splits the corpus into code/ and architecture/, and selects the snippet size ceiling.
status: draft
created: 2026-09-06
updated: 2026-09-06
author: ernst
tags: [adr, schema, corpus, layout]
category: adr
related:
  - docs/002-snippet-design.md
  - docs/adr/002-one-smell-per-markdown-file.md
  - docs/adr/010-monorepo-with-language-scoped-corpus.md
---

# Architecture Group With A Larger Ceiling

## Context

The 15-line ceiling was set to keep snippets legible, to force reconstruction rather than pasting, and to keep
architecture-level anti-patterns out of a schema built for passages of code
([ADR 002](./002-one-smell-per-markdown-file.md), [ADR 009](./009-reconstructed-snippets-and-licensing.md)).

The first two goals hold. The third turned out to exclude smells the corpus wants. A subsystem assembled by
every one of its callers, a dependency pointing the wrong way, a layer that exists and is bypassed — these are
ordinary review findings with a named fix, and they fit the existing schema fine: one signature, one severity,
one near miss, one `## Better`. What they do not fit is the ceiling, because the evidence is a second call site
that repeats the first. Cut them to 15 lines and the duplication — the actual smell — disappears from the
snippet.

Three ways to allow the length were considered. A per-file frontmatter flag such as `extended_snippet: true`,
which puts the limit inside the file being limited and makes every contributor argue about it. A single global
ceiling raised to 40, which lets every snippet drift longer and loses the pressure that keeps `code/` sharp. Or
a directory, which is legible from the path.

## Decision

Insert a group directory below the language: `snippets/<language>/<group>/<slug>.md`, with two values, `code`
and `architecture`. The directory list is closed and lives in `validate.py` as `SNIPPET_LINES`, which maps each
group to its ceiling: 15 lines for `code`, 40 for `architecture`.

The group is a size ceiling and nothing else. It is not a frontmatter field, is not in the catalog, and no
retrieval path branches on it — a smell's meaning does not change with the number of lines needed to show it.
Everything else in the schema applies identically to both groups.

## Consequences

- Architecture-level smells are in scope, and the corpus can name the pattern-shaped findings that reviewers
  actually raise. `architecture/` opens with one entry per Gang of Four pattern — 22 files, each describing the
  code that the pattern is the answer to, credited `source: refactoring.guru`.
- A corpus with an entry per pattern can be read as "not using the pattern is a smell", which would turn the
  server into a generator of speculative indirection. The guard is `distinguish`: every one of the 22 names the
  case where the plain code is right and the pattern is overbuilding. This is the field to review hardest in
  those entries, and the reason a reviewer should resist adding pattern entries without one.
- The ceiling is visible in the path, so it is chosen once when the file is created rather than negotiated per
  snippet, and `code/` keeps the pressure that makes its entries readable at a glance.
- Every existing snippet moved to `snippets/python/code/`. Identifiers are filenames, so nothing citing a smell
  broke, and no aliases were needed ([ADR 008](./008-filename-as-identifier-with-aliases.md)).
- Two globs had to widen to `*/*/*.md`, in `validate.py` and in the server's reading layer. That the change was
  two lines is a consequence of identity being the filename rather than the path.
- The group is a filing decision a contributor can get wrong, and the validator cannot catch it: a 40-line
  entry in `architecture/` that a 12-line snippet would have shown is a review question, not a schema one.
- A third group would be cheap to add, which is a risk. Groups are ceilings, not subject areas; anything that
  wants to say what a smell is *about* belongs in `topic` or `tags`.

## Status

Accepted — 2026-09-06.
