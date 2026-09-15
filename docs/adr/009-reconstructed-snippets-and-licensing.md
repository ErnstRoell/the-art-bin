---
title: Snippets Are Reconstructions, Licensed CC0
description: Snippets must be small, unrecognisable reconstructions; the corpus is CC0 and the server MIT.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, licensing, provenance, contributions]
category: adr
related:
  - docs/002-snippet-design.md
  - docs/adr/011-architecture-group-with-a-larger-ceiling.md
---

# Snippets Are Reconstructions, Licensed CC0

## Context

This is a public repository collecting real-world bad code. The obvious contribution flow — paste the awful
thing you just found — carries two problems. Legally, code pasted from an employer's codebase is unlicensed
third-party material republished here. Socially, a recognisable snippet is a colleague's work published as an
example of what not to do.

Licensing needed deciding too, and the corpus and the server have different natures: the corpus is data whose
purpose is to be ingested, including by model trainers; the server is software.

## Decision

Snippets are **minimal reconstructions written to illustrate a smell**, never excerpts of any real codebase, and
this is stated in `README.md` and `CONTRIBUTING.md`. The snippet ceiling and the one-smell-per-snippet rule are
enforced in CI and are what make that claim true in practice rather than merely asserted — no real code is that
small or that single-purpose, so the constraints force rewriting. ([ADR 011](./011-architecture-group-with-a-larger-ceiling.md)
raised the ceiling to 40 lines for `architecture/`, which is still far below any real call site.)

`source` is optional credit for the contributor of the smell. It is not a code provenance field.

`snippets/` is licensed CC0. The server under `src/` is licensed MIT. Both carry the standard no-warranty,
no-liability terms, pointed at from `README.md`.

## Consequences

- Contributors cannot paste. They must understand a smell well enough to rebuild a minimal version of it, which
  raises quality alongside safety.
- The non-liability position is honest: the editorial constraints and the legal claim reinforce each other
  instead of the disclaimer standing alone.
- CC0 rather than CC-BY because attribution requirements are friction for exactly the consumers the corpus is
  meant to serve. The cost is that reuse carries no obligation to credit the project.
- No mechanism verifies that a snippet is a reconstruction; it rests on the size ceiling and reviewer judgement.
- Hard to reverse. Relicensing a corpus with outside contributions requires their agreement, so CC0 is
  effectively permanent from the first accepted contribution.

## Status

Accepted — 2026-09-04.
