---
title: The Filename Is The Identifier
description: A smell's slug is its filename, with an aliases field keeping old identifiers resolvable.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, schema, identity]
category: adr
related:
  - docs/002-snippet-design.md
---

# The Filename Is The Identifier

## Context

The server returns identifiers, and calling models will quote them in review comments and commit messages, so
identifiers leak outside the repository. Meanwhile files get renamed as understanding of a smell improves.

The options were an immutable `id` field decoupled from the filename, the filename alone with renames simply
breaking old references, or the filename plus a record of former names.

## Decision

The filename is the identifier. There is no `id` frontmatter field — duplicating the slug would only create
something able to drift out of sync. Slugs match `[a-z0-9-]+` and are named after the smell rather than the fix:
`mutable-default-argument`, not `use-none-default`.

An optional `aliases` list records former slugs. `get_smells` resolves aliases transparently and reports the
canonical identifier in `id` with the alias in `resolved_from`, so anything a model cites afterwards is current.

## Consequences

- A rename is a `git mv` plus one alias entry. No identifier ceremony for a problem the project does not have.
- Validation must check that no alias collides with any slug or any other alias, or resolution becomes
  ambiguous. This is cheap now and impossible to add cleanly once collisions exist.
- Aliases accumulate indefinitely, since removing one breaks references it was created to preserve.
- Naming after the smell rather than the fix keeps identifiers stable when opinions about the remedy change,
  which is more often than opinions about the problem.

## Status

Accepted — 2026-09-04.
