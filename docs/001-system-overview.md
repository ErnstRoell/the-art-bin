---
title: System Overview
description: What The Art Bin is, the three parts it is made of, and the reasoning behind the shape.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [architecture, overview, mcp, corpus]
category: architecture
related:
  - docs/002-snippet-design.md
  - docs/003-mcp-api-overview.md
  - CONTEXT.md
---

# System Overview

The Art Bin is a curated corpus of bad Python code. Each file describes one **smell** — a single named way that
code goes wrong — small enough to read at a glance and structured enough for a machine to work with. An MCP
server exposes the corpus so that an LLM reviewing a real codebase can ask "does anything here resemble a known
smell?" and get back specific, opinionated answers rather than generic advice.

## Why This Exists

Linters already catch the mechanically detectable defects. `ruff` and Semgrep will find bare excepts and unused
imports forever, and nothing here competes with them. What no linter ships is *taste*: the pet peeves, the
house style, the patterns that run fine and will keep running fine but that a particular team refuses to accept.
That knowledge normally lives in reviewers' heads and leaks out one PR comment at a time.

The Art Bin makes that knowledge addressable. It is a place to write down "we don't do this, and here is what
we do instead" once, in a form an LLM can consult against real code. See
[ADR 001](./adr/001-corpus-as-queryable-knowledge-base.md) for the decision to treat the corpus as a queryable
knowledge base rather than a style guide.

## The Three Parts

### The Corpus

A directory of markdown files, one per smell, at `snippets/<language>/<group>/<slug>.md`. Python is the only
language today; the path carries the language so that adding another later is a new directory rather than a
migration. The group is `code` or `architecture`, and selects only the snippet size ceiling
([ADR 011](./adr/011-architecture-group-with-a-larger-ceiling.md)).
Each file holds YAML frontmatter (the machine-readable part) and a short body: the offending snippet, why it is
bad, and the corrected version. The corpus is the source of truth and the actual product — everything else is
machinery around it. The full anatomy is in [Snippet Design](./002-snippet-design.md).

### The Catalog

A single generated file summarising every smell: identifier, one-sentence signature, severity, category, topic,
tags, and keywords. It is small on purpose — roughly thirty tokens per smell, so a corpus of 150 smells is about
5,000 tokens and fits comfortably in a prompt. The catalog is committed to the repository rather than assembled
at startup, so the server needs no build step and no model to be useful
([ADR 007](./adr/007-committed-generated-catalog.md)).

### The MCP Server

A thin service over the corpus, exposing the catalog and full-record fetches as MCP tools. It performs no
analysis: it does not read the user's code, score anything, or decide what matches. The calling LLM does that.
See [MCP API Overview](./003-mcp-api-overview.md).

## How A Review Actually Works

Retrieval is two-phase, and the split is the central design idea.

1. The LLM has the user's code in context. It fetches the whole catalog in one call.
2. It reads the signatures and keywords and shortlists the handful of smells that might plausibly apply.
3. It fetches the full records for those few — snippet, reasoning, corrected version, and the near-miss
   description that says when the pattern is *acceptable*.
4. It decides. Any finding it reports is grounded in a specific corpus entry it can cite by identifier.

Shortlisting is cheap and lexical; confirmation is expensive and precise. Nothing is spent reading full records
for smells that were never candidates.

## Why Not Vector Search

The obvious design is to embed each bad snippet and compare it against chunks of the user's code. It fails in a
specific and predictable way: **code embeddings capture topic, not defect.** Consider these two fragments.

```python
try:
    load(path)
except:
    pass
```

```python
try:
    load(path)
except OSError:
    log.warning("could not load %s", path)
    raise
```

Same tokens, same shape, same subject matter, near-identical vectors — and one is a smell while the other is
correct code. Similarity search returns both with roughly equal confidence, and the caller has no way to tell
them apart. High recall, unusable precision.

The catalog-first design sidesteps this because the matcher is the LLM, and it has the target code fully in
context — exactly the information an embedding query discards. Two consequences follow: the corpus needs a field
saying explicitly what the *near miss* looks like
([ADR 005](./adr/005-require-distinguish-and-better.md)), and the system needs no embedding model, no vector
store, and no API key. See [ADR 006](./adr/006-catalog-first-retrieval-no-embeddings.md).

Search becomes necessary only when the catalog outgrows a prompt. At that point the next step is keyword and
metadata search over the existing fields — not embeddings.

## Repository Layout

```text
/
├── CONTEXT.md              # glossary — the project's vocabulary
├── README.md
├── TAXONOMY.md             # the closed lists for category and topic
├── TEMPLATE.md             # skeleton for a new smell
├── CONTRIBUTING.md
├── catalog.json            # generated, committed
├── validate.py             # schema and constraint checks, run in CI
├── docs/
│   ├── 001-system-overview.md
│   ├── 002-snippet-design.md
│   ├── 003-mcp-api-overview.md
│   └── adr/
├── snippets/
│   └── python/
│       ├── code/           # 15-line ceiling
│       │   └── <slug>.md
│       └── architecture/   # 40-line ceiling
│           └── <slug>.md
└── server/                 # the MCP server
```

Corpus and server live in one repository while the schema is still moving, so that "add a field" and "teach the
server the field" can be one commit ([ADR 010](./adr/010-monorepo-with-language-scoped-corpus.md)).

## Scope Boundaries

The following are deliberate exclusions, not gaps:

- **The server does not judge.** It serves records. All matching and reporting is the caller's job.
- **Snippets are reconstructions, never pasted from real codebases.** This is a legal and social constraint as
  much as an editorial one ([ADR 009](./adr/009-reconstructed-snippets-and-licensing.md)).
- **The snippet ceiling is hard.** Fifteen lines in `code/`, forty in `architecture/` for the few smells that
  are a relationship between components rather than a passage of code. Anything larger is a system, not a
  smell, and does not fit this schema.
- **No embeddings, no vector store, no scoring model.**

## Related Documents

- [Snippet Design](./002-snippet-design.md) — the file format and its constraints
- [MCP API Overview](./003-mcp-api-overview.md) — the tool surface
- [Architecture Decision Records](./adr/) — the decisions behind all of the above
- [CONTEXT.md](../CONTEXT.md) — the project glossary
