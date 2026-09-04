---
title: MCP API Overview
description: The MCP tool surface over the corpus — catalog listing, record fetching, and the two-phase contract.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [mcp, api, reference, server]
category: reference
related:
  - docs/001-system-overview.md
  - docs/002-snippet-design.md
---

# MCP API Overview

The server is a thin read-only interface over the corpus. It exposes three tools: one that returns the whole
catalog, one that returns full records for specific smells, and one that returns the taxonomy. It performs no
analysis of the caller's code — matching is the calling model's job
([ADR 001](./adr/001-corpus-as-queryable-knowledge-base.md)).

## Overview

The server reads `catalog.json` for listings and the markdown files under `snippets/` for full records. It is
stateless, needs no configuration, and requires no network access, embedding model, or API key. Transport is
stdio.

## The Two-Phase Contract

Every tool exists to serve one of two phases. Keeping them separate is what makes a single-call catalog viable
at all — the catalog is small because full records are deliberately not in it
([ADR 006](./adr/006-catalog-first-retrieval-no-embeddings.md)).

1. **Shortlist.** One `list_smells` call. The model reads signatures and keywords against the code already in
   its context and picks the few candidates worth investigating. Cheap and lexical.
2. **Confirm.** One `get_smells` call for those candidates. The model reads each snippet, its reasoning, its
   corrected version, and critically its `distinguish` line, then decides. Precise and narrow.

A model that skips phase one and guesses identifiers will miss smells. A model that fetches every record in
phase two has wasted the design.

## API

### `list_smells`

Returns the catalog: one compact entry per smell. Roughly 30 tokens per entry, so the whole corpus fits in a
prompt at current and projected size.

**Parameters** — all optional; omit everything to get the full catalog, which is the expected default.

| Parameter | Type | Description |
| --- | --- | --- |
| `severity` | `string[]` | Restrict to `bug`, `trap`, and/or `taste` |
| `category` | `string[]` | Restrict to consequence categories |
| `topic` | `string[]` | Restrict to Python-feature topics |
| `language` | `string` | Defaults to `python` |
| `python_version` | `string` | Return only smells whose `python` range includes this version |

**Response**

```json
{
  "schema_version": 1,
  "language": "python",
  "count": 2,
  "smells": [
    {
      "id": "mutable-default-argument",
      "signature": "A function default is a list or dict, so one object is shared across every call.",
      "severity": "trap",
      "category": "correctness",
      "topic": "mutability",
      "tags": ["defaults", "functions"],
      "keywords": ["=[]", "={}", "default argument", "append"]
    },
    {
      "id": "bare-except-pass",
      "signature": "An except clause with no type and an empty body discards every error silently.",
      "severity": "bug",
      "category": "correctness",
      "topic": "exceptions",
      "tags": ["error-handling"],
      "keywords": ["except:", "pass", "try"]
    }
  ]
}
```

`distinguish` is deliberately absent here. It belongs to the confirm phase, and including it would roughly
double catalog size for information the model cannot yet use.

### `get_smells`

Returns full records for specific smells. Batched, because phase two fetches a handful at once.

**Parameters**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ids` | `string[]` | yes | Slugs or aliases. Aliases resolve transparently. |

**Response**

```json
{
  "schema_version": 1,
  "smells": [
    {
      "id": "mutable-default-argument",
      "resolved_from": null,
      "signature": "A function default is a list or dict, so one object is shared across every call.",
      "distinguish": "Fine when the default is immutable, or when shared state is the documented intent.",
      "severity": "trap",
      "category": "correctness",
      "topic": "mutability",
      "tags": ["defaults", "functions"],
      "keywords": ["=[]", "={}", "default argument", "append"],
      "language": "python",
      "python": ">=3.0",
      "added": "2026-09-04",
      "source": "ernst",
      "title": "Mutable default argument",
      "snippet": "def add_item(item, basket=[]):\n    basket.append(item)\n    return basket",
      "why_bad": [
        "The list is created once, at definition time, and outlives the call.",
        "Callers who omit `basket` silently share state with every previous caller."
      ],
      "better": "def add_item(item, basket=None):\n    basket = [] if basket is None else basket\n    basket.append(item)\n    return basket"
    }
  ],
  "unknown": ["not-a-real-slug"]
}
```

Unknown identifiers are reported in `unknown` rather than raising. A partial answer is more useful to a model
mid-review than a failed call, and a hallucinated slug should not discard the valid ones alongside it. When an
alias was used, `resolved_from` carries the alias and `id` carries the canonical slug, so anything the model
cites afterwards is the current identifier.

### `get_taxonomy`

Returns the closed lists with corpus counts, so a model can construct sensible `list_smells` filters without
guessing at valid values.

**Parameters** — none.

**Response**

```json
{
  "schema_version": 1,
  "category": {"correctness": 12, "security": 3, "readability": 8},
  "topic": {"exceptions": 5, "mutability": 4, "naming": 6},
  "severity": {"bug": 9, "trap": 7, "taste": 7}
}
```

## Non-Goals

- **No `analyze_code` tool.** Nothing in this API accepts source code as input. Accepting code would mean the
  server has to match, which means either shipping an embedding model or reimplementing a linter — both
  rejected. It also means user code stops crossing a process boundary it has no reason to cross.
- **No ranking or scoring.** The server returns records, not confidence values. Confidence is the calling
  model's judgement, made with the target code in context.
- **No write tools.** Contributions arrive as pull requests, not API calls.
- **No search tool yet.** Deferred until the catalog stops fitting in a prompt, at which point the first move is
  keyword and metadata search over `keywords` and `tags` — not vectors.

## Usage Contract For The Calling Model

The tool descriptions should state this explicitly, since the value of the corpus depends on it:

- Fetch the catalog before naming any smell. Do not guess identifiers.
- Read `distinguish` before reporting a finding. It exists to describe the legitimate variant, and skipping it
  is how correct code gets flagged.
- Cite the smell `id` in every finding, so a reader can go read the entry.
- Respect `severity`. A `taste` finding is a house-style preference and should be reported as one, not as a bug.

## Versioning

`schema_version` appears in every response and tracks the frontmatter schema, not the server release. It
increments only on a breaking field change — a removal or a type change. Additive fields do not bump it.

## Related Documents

- [System Overview](./001-system-overview.md) — the reasoning behind this surface
- [Snippet Design](./002-snippet-design.md) — the fields these responses carry
