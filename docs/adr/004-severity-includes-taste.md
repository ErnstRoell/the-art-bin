---
title: Severity Spans Bug, Trap, And Taste
description: Subjective preferences are in scope, but every smell must declare what it actually costs.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, schema, scope]
category: adr
related:
  - docs/002-snippet-design.md
---

# Severity Spans Bug, Trap, And Taste

## Context

The corpus could restrict itself to objective defects — mutable defaults, swallowed exceptions,
string-concatenated SQL — or it could include matters of taste, which is what "pet peeves and special
snowflakes" actually describes. Excluding taste would remove the corpus's reason to exist, since linters already
cover the mechanical cases. Including it without distinction is worse: an LLM told "never use single-letter
names" with the same force as "never concatenate SQL" will misprioritise both, and the corpus loses authority.

## Decision

Both are in scope, and every smell declares a required `severity`:

- `bug` — wrong today; produces incorrect behaviour as written.
- `trap` — works today, bites later; correct until a condition changes.
- `taste` — works and keeps working, but reads badly.

## Consequences

- Consumers can filter by cost, and reported findings can be phrased proportionately. A `taste` finding is a
  house-style preference and should be presented as one.
- `trap` earns its place as a separate value because it is the most common and least served case: code that
  passes review, passes tests, and fails months later.
- Contributors must judge severity, and some judgements will be contested. That is preferable to a corpus where
  the distinction is invisible.
- This field is the most annoying to retrofit — it cannot be inferred from the snippet — so it is required from
  the first entry.
- Because `taste` entries assert a preference rather than a fact, they carry the strongest obligation to state
  the alternative. See [ADR 005](./005-require-distinguish-and-better.md).

## Status

Accepted — 2026-09-04.
