---
title: Require A Near-Miss Description And A Corrected Version
description: Every smell must state what the acceptable variant looks like and what to write instead.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, schema, precision]
category: adr
related:
  - docs/002-snippet-design.md
---

# Require A Near-Miss Description And A Corrected Version

## Context

Because matching is delegated to the calling LLM ([ADR 001](./001-corpus-as-queryable-knowledge-base.md)), the
dominant failure mode is not missing a smell — it is flagging correct code that merely resembles one. Swallowed
exceptions and properly handled exceptions look alike at a glance: same keywords, same shape, same subject.
Nothing in a snippet-plus-explanation entry tells a reader where the boundary is.

Separately, remediation had to be decided. A model can often infer the fix, so a corrected version could be
treated as optional decoration.

## Decision

Two required fields.

`distinguish` is a one-sentence description of the near miss that is *not* the smell — "fine when the exception
is re-raised, or when the handler genuinely handles it."

`## Better` is a required body section for every smell, regardless of severity.

## Consequences

- `distinguish` is the corpus's main defence against false positives, and the field no linter or general-purpose
  model provides. It is fetched during the confirm phase and the calling model is instructed to read it before
  reporting anything.
- Deliberately kept out of the catalog: it is useless during shortlisting and would roughly double catalog size.
- Requiring `## Better` uniformly is partly redundant for `bug` entries, where the fix is near-obvious. It is
  retained anyway, because for `taste` entries the alternative *is* the content — "I dislike this" is
  unactionable without "write this instead" — and one uniform rule beats a conditional one.
- Contribution bar rises. Someone who cannot write the near miss has not understood their own smell well enough
  to add it, which is the intended filter.
- The corrected version doubles as a negative example: a query that matches the smell snippet should not also
  match the `## Better` snippet, which is a usable test of entry quality.

## Status

Accepted — 2026-09-04.
