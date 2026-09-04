---
title: Catalog-First Retrieval Instead Of Vector Search
description: Return the whole catalog and let the calling LLM shortlist; no embeddings, no vector store.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, retrieval, mcp, architecture]
category: adr
related:
  - docs/001-system-overview.md
  - docs/003-mcp-api-overview.md
---

# Catalog-First Retrieval Instead Of Vector Search

## Context

The intended use is similarity search: an LLM asks whether code in front of it resembles a known smell. The
obvious implementation embeds each snippet and compares against chunks of the target code.

That fails in a specific way. **Code embeddings capture topic, not defect.** `try: load(path) except: pass` and
`try: load(path) except OSError: log.warning(...); raise` are near-identical vectors — same tokens, same shape,
same subject — yet one is a smell and one is correct. Similarity search returns both with comparable confidence
and the caller cannot tell them apart. High recall, unusable precision.

The corpus is also small: tens of entries now, a few hundred at maturity. At roughly thirty tokens per catalog
entry, the entire catalog fits in a prompt.

## Decision

Retrieval is two-phase and index-free.

1. `list_smells` returns the whole catalog — identifier, signature, severity, category, topic, tags, keywords.
   The calling model reads it against code already in its context and shortlists candidates.
2. `get_smells` returns full records for those candidates, including `distinguish`, and the model decides.

No embedding model, no vector store, no ranking. Each entry carries `keywords` — literal tokens likely to appear
in offending code — as lexical hooks for shortlisting and as the index a future keyword search would use.

## Considered Options

Vector similarity was rejected for the precision reason above. Keyword or full-text search over metadata was
deferred: it is the correct next step, but unnecessary while the catalog fits in a prompt.

## Consequences

- The matcher is the LLM, which has the target code fully in context — precisely the information a vector query
  discards. This is a capability gain, not just a simplification.
- Zero configuration: no API key, no model download, no network. This materially affects whether the server gets
  installed at all.
- Scaling limit is explicit. Past roughly 150 entries the catalog stops being comfortable in a prompt, and the
  first response is keyword and metadata search over `keywords` and `tags` — not embeddings.
- Result quality depends on `signature` and `keywords` being written well, so those fields carry weight that
  would otherwise sit in an embedding model.
- Two round trips per review instead of one.

## Status

Accepted — 2026-09-04.
