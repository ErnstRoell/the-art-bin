---
title: Monorepo With A Language-Scoped Corpus
description: Corpus and server share one repository, and the corpus path carries the language from day one.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, repository, layout]
category: adr
related:
  - docs/001-system-overview.md
  - docs/adr/011-architecture-group-with-a-larger-ceiling.md
---

# Monorepo With A Language-Scoped Corpus

## Context

Two layout questions. First, whether the corpus and the MCP server share a repository: the corpus is public,
contributor-facing markdown, while the server is versioned software with dependencies, and a data-only
repository is easier to fork and PR against. Second, whether the corpus is flat or language-scoped: Python is
the only language planned, but the project is not inherently Python-specific and demand for others is plausible.

## Decision

One repository containing both `snippets/` and `server/`.

Corpus files live at `snippets/<language>/<slug>.md`, so Python content starts at `snippets/python/`. Each file
also carries a `language` field, making it self-describing outside its directory. ([ADR 011](./011-architecture-group-with-a-larger-ceiling.md)
later inserted a group directory below the language, leaving the language-scoping decision here intact.)

## Consequences

- Schema changes are atomic: "add a field" and "teach the server the field" are one commit. This matters most
  now, while the schema is still moving, and matters less as it settles.
- A contributor adding one markdown file sees a `server/` directory they have no reason to touch. Acceptable
  friction; `CONTRIBUTING.md` should point straight at `snippets/python/` and `TEMPLATE.md`.
- Adding a second language is a new directory, not a migration of every path. One directory of cost today buys
  that.
- The `language` field is redundant with the path. Kept deliberately, so an extracted or transmitted record
  remains complete.
- If contributor volume ever justifies a pure data repository, splitting the corpus out is the graduation path,
  with the server depending on it as a pinned dependency.

## Status

Accepted — 2026-09-04.
