---
title: Every Claim Traced To A Source
description: Each smell's claims are tied to the published passage that states them, deep-linked and quoted, in a per-language sources page.
status: draft
created: 2026-09-30
updated: 2026-09-30
author: jeremy
tags: [adr, corpus, sources]
category: adr
related:
  - docs/sources.md
  - docs/adr/004-severity-includes-taste.md
  - docs/adr/009-reconstructed-snippets-and-licensing.md
---

# Every Claim Traced To A Source

## Context

An entry makes claims: that a mechanism goes wrong in a stated way, and that the fix avoids it. The corpus is
read by models that will repeat those claims in reviews, so a wrong one propagates. Until now nothing recorded
where a claim came from. The `source` field is contributor credit ([ADR 009](./009-reconstructed-snippets-and-licensing.md)),
and on the architecture entries it named refactoring.guru without saying where on it.

## Decision

**Each language has a sources page**, `docs/<language>-sources.md`. It has one row per claim, giving the entry,
the claim, a link and a verbatim quote of at most 30 words.

**The link lands on the passage.** It uses a section anchor when one is close enough, and a `#:~:text=` fragment
when none is. A link to the top of a long page does not count as a source.

**A claim no source states is either cut, or marked.** A claim a source contradicts is corrected in the entry.
A style preference is marked `house taste`, which is the case `severity: taste` exists for
([ADR 004](./004-severity-includes-taste.md)). The page lists what it leaves unsourced.

**`source` keeps its meaning.** It stays contributor credit, or the primary reference where an entry already
used it that way. Provenance lives in the sources pages, not in frontmatter.

## Consequences

- A new smell is not finished until its rows are in the sources page. `get_smells` serves them as each
  record's `sources`, and the server's tests fail when an entry has none.
- The rows are checked against the downloaded page: the anchor exists, the fragment's text is on the page, and
  the quote appears verbatim. That check is not in CI, because it needs the network and the pages change
  underneath it. Re-running it is how rot gets found.
- Writing the pages corrected ten entries whose claims their sources did not support.

## Status

Accepted — 2026-09-30.
