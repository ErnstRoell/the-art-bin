---
title: One Smell Per Markdown File
description: The unit of the corpus is a single smell in a single markdown file with YAML frontmatter.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, schema, corpus]
category: adr
related:
  - docs/002-snippet-design.md
---

# One Smell Per Markdown File

## Context

Three groupings were plausible. One file per **smell**, illustrated by the smallest snippet that demonstrates it.
One file per **specimen** — a real chunk of code encountered in the wild, which may exhibit several smells at
once. One file per **theme**, such as an `exceptions.md` holding a dozen numbered snippets.

The requirement that each file carry its own category, tags, and date effectively settled this: the moment a
file holds several smells, frontmatter cannot describe them, because there is no single severity, category, or
near-miss to state.

## Decision

One file is one smell, at `snippets/<language>/<slug>.md`, with YAML frontmatter for machine-readable fields and
exactly three body sections: the snippet, why it is bad, and the corrected version.

Snippets must satisfy `ast.parse` but need not run. Requiring runnable code would force scaffolding into
snippets, which dilutes the illustration; requiring parseable code costs a one-line check and keeps the corpus
mechanically processable.

## Consequences

- Metadata attaches to the unit it actually describes.
- A snippet demonstrating several problems must be split, and if the problems only ever occur together, that
  combination needs its own name and entry.
- Entries deduplicate naturally, since the same smell has one home regardless of how many times it is met.
- Specimens — real annotated code exhibiting several smells — are not supported. If wanted later, they belong in
  a separate tree that references smells by identifier rather than restating them.
- The corpus will contain many small files. Navigation therefore depends on the catalog and taxonomy rather than
  on directory browsing.

## Status

Accepted — 2026-09-04.
