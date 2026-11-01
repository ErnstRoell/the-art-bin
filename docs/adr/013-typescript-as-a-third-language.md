---
title: TypeScript As A Third Language
description: TypeScript joins the corpus under snippets/typescript/, covering plain JavaScript too, parse-checked by the tsc parser, with every entry traced to a published source.
status: draft
created: 2026-09-30
updated: 2026-09-30
author: jeremy
tags: [adr, schema, corpus, language]
category: adr
related:
  - docs/adr/012-rust-as-a-second-language.md
  - docs/typescript-sources.md
---

# TypeScript As A Third Language

## Context

[ADR 012](./012-rust-as-a-second-language.md) listed what a third language costs: a directory, a `LANGUAGES`
entry, a scaffold entry, a parse check and a version filter. TypeScript is that language, and it is the first
one whose corpus has to serve two dialects — most TypeScript smells are JavaScript smells with annotations on
top, and most of the projects that will query it mix the two.

## Decision

**One language, `typescript`, covers JavaScript.** TypeScript is a superset, so a JavaScript snippet is a valid
TypeScript snippet and parses under the same check. Entries that apply to plain JavaScript carry the
`javascript` tag; entries that only exist because of the type system (`any`, `as`, `!`, `enum`) do not. A
separate `javascript` language was rejected: it would split counterpart entries across two directories and make
a reviewer of a mixed codebase query twice.

**The version field is `typescript:`** and counts compiler versions, like `rust:` counts toolchains. It is raised
when the *fix* needs a newer compiler or `lib` — `satisfies` is `>=4.9`, `??` is `>=3.7`.

**Snippets are parsed by the `tsc` parser alone.** The validator loads the compiler API from the `tsc` on
`PATH` and fails a block only on `parseDiagnostics`, first as `.ts` and then as `.tsx`, so React snippets need no
fence tag of their own. Unresolved imports and type errors never reach the parser, which keeps the bar where
`ast.parse` sets it. CI installs `typescript@5` with npm.

**Every entry names its source.** The code group opens with 63 smells and the architecture group with the same
22 Gang of Four entries as Python and Rust. Each entry's `source` names the primary reference it was checked
against — typescript-eslint, MDN, the TypeScript handbook, Node.js, React, OWASP, refactoring.guru — and
[`docs/typescript-sources.md`](../typescript-sources.md) lists the URL for each one, plus a book or blog where
one supports it.

## Consequences

- The corpus passes the roughly 150 entries at which [ADR 006](./006-catalog-first-retrieval-no-embeddings.md)
  says an unfiltered catalog stops being comfortable in a prompt. A reviewer that passes `language` reads 85
  TypeScript entries, which is what the server instructions already tell it to do; an unfiltered `list_smells`
  is now the expensive call.
- Validating TypeScript entries needs `node` and `tsc` on `PATH`; the validator says so rather than passing them.
- React entries live in the language corpus rather than a framework one. If framework smells grow past a
  handful, they want a tag convention or a group of their own.
- `source` on these entries is a reference, not a contributor handle. Python and Rust code entries still use it
  for credit.

## Status

Accepted — 2026-09-30.
