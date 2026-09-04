---
title: Two-Axis Taxonomy With Open Tags
description: Classify smells on a consequence axis and a Python-feature axis, with free-form tags alongside.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, taxonomy, schema]
category: adr
related:
  - docs/002-snippet-design.md
---

# Two-Axis Taxonomy With Open Tags

## Context

A single `category` field forces a choice of axis, and the two candidate axes are both useful for different
reasons. Classifying by **consequence** (`correctness`, `readability`, `security`) matches what a reviewer wants
to filter on. Classifying by **Python feature** (`exceptions`, `mutability`, `typing`) matches what the code
looks like, which is what narrows candidates during shortlisting.

These are not redundant. A mutable default argument is `mutability` by feature and `correctness` by consequence,
and collapsing them loses one of those queries.

## Decision

Three fields. `category` is one value from a closed list on the consequence axis. `topic` is one value from a
closed list on the Python-feature axis. `tags` is open-ended and may be empty.

Both closed lists live in `TAXONOMY.md`. Adding a value is a deliberate pull request that edits that file.

Seed values are `correctness`, `security`, `performance`, `readability`, `maintainability`, `testability` for
category; `exceptions`, `mutability`, `typing`, `naming`, `functions`, `classes`, `control-flow`, `imports`,
`strings`, `io`, `concurrency`, `stdlib-misuse` for topic.

## Considered Options

A single free-form tag list was rejected: it is what contributors reach for, and it fragments within a dozen
entries — `error-handling` and `exceptions` and `errors` all appear and none of them filter reliably.

A `style` category was rejected because `severity: taste` already carries that axis, and having both invites the
same smell being filed two contradictory ways.

## Consequences

- Two required decisions per contribution, both validated against the closed lists, so a typo fails CI rather
  than silently creating a category of one.
- The lists will need curation. `stdlib-misuse` is a deliberate escape hatch so contributors are not forced into
  a bad fit; if it exceeds roughly 15% of the corpus it should be split.
- Retrofitting a third axis later would mean touching every file, so the axes are effectively fixed.

## Status

Accepted — 2026-09-04.
