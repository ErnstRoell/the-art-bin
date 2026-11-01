---
title: Rust As A Second Language
description: Rust joins the corpus under snippets/rust/, with a per-language version field, a rustc parse check, and language carried into the catalog.
status: draft
created: 2026-09-25
updated: 2026-09-25
author: jeremy
tags: [adr, schema, corpus, language]
category: adr
related:
  - docs/002-snippet-design.md
  - docs/003-mcp-api-overview.md
  - docs/adr/010-monorepo-with-language-scoped-corpus.md
  - docs/adr/011-architecture-group-with-a-larger-ceiling.md
---

# Rust As A Second Language

## Context

[ADR 010](./010-monorepo-with-language-scoped-corpus.md) put the language in the path so that a second language
would be a new directory rather than a migration. Rust is that language. The directory is the easy part; three
places in the schema were written as though Python were the only language and have to say otherwise.

The version range was a field named `python`. The parse check was `ast.parse`. And the catalog carried no
`language`, because a single-language catalog did not need one — the `language` filter on `list_smells` either
returned everything or nothing.

## Decision

Rust entries live at `snippets/rust/<group>/<slug>.md`, with the same groups, ceilings, taxonomy and sections as
Python. The architecture group opens with the same 22 Gang of Four entries, described in Rust terms.

**The version field is named after the language.** A Python entry carries `python: ">=3.9"`, a Rust entry
`rust: ">=1.45"`. The validator requires the field matching `language` and rejects the other as unknown. One
generic `version` field was considered and rejected: `">=1.45"` means nothing without knowing which toolchain it
counts, and a named field makes a misfiled entry fail loudly.

**Rust snippets are parsed by `rustc`.** Each block is compiled with `--emit=metadata` as a crate, and failing
that as the body of a function, so both item-level and statement-level snippets pass. Every error about what
the snippet leaves out — unresolved crates, macros, attributes, missing files, type errors — is ignored, which
keeps the bar where `ast.parse` sets it for Python: the code must be the language, not build. Validating Rust
entries therefore needs a Rust toolchain on `PATH`, and CI installs one.

**`language` is a catalog field.** Every catalog entry carries it, the top-level `language` becomes a list, and
`list_smells` filters on it per smell. With no `language` argument the server returns both languages. A
`python_version` or `rust_version` filter implies its language; giving both returns each language checked
against its own range.

**Identifiers stay global.** A Rust smell and its Python counterpart get different slugs
(`float-compared-with-double-equals`, `float-equality-comparison`), and the validator rejects a collision
across languages. Identity is the filename ([ADR 008](./008-filename-as-identifier-with-aliases.md)), and a
`get_smells` call names ids without a language.

## Consequences

- A third language is a directory, a `LANGUAGES` entry in `validate.py`, a scaffold entry in `new_smell.py`, a
  parse check, and a `<language>_version` filter on the server.
- Contributors without Rust installed cannot validate Rust entries locally; the validator says so rather than
  passing them.
- The `rustc` check is looser than `ast.parse` by design. A snippet with a type error passes, and a few parser
  errors that carry an error code are ignored along with the resolution errors.
- The taxonomy is shared. `topic` values were written for Python and read slightly differently in Rust —
  `exceptions` covers `Result` propagation, `typing` covers traits — and the descriptions in `TAXONOMY.md` were
  widened to say so rather than adding Rust-only values.
- `get_taxonomy` counts both languages together.
- Counterpart smells in the two languages are not linked. A reviewer reading one does not learn the other exists.

## Status

Accepted — 2026-09-25.
