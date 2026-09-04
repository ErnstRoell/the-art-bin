---
title: Corpus As A Queryable Knowledge Base, Not A Style Guide
description: The corpus is built to be queried by an MCP server; the server serves records and the LLM judges.
status: draft
created: 2026-09-04
updated: 2026-09-04
author: ernst
tags: [adr, architecture, mcp]
category: adr
related:
  - docs/001-system-overview.md
---

# Corpus As A Queryable Knowledge Base, Not A Style Guide

## Context

The original framing was a collection of pet peeves "so your LLM can learn what not to do." That admits several
readings: prose guidance injected into a system prompt, a set of eval fixtures with known verdicts, or a
retrieval corpus consulted per review. Each wants a different file: guidance wants imperative prose, evals want
expected answers, retrieval wants findability against code the corpus has never seen.

We also had to decide how much work the server does. It could accept source code and return findings, or it
could serve corpus records and leave matching to the caller.

## Decision

The corpus is a retrieval knowledge base consumed by an MCP server. Every file is a document whose primary job
is to be findable by resemblance to unfamiliar code, which is why the schema is machine-readable and the entries
are short.

The server serves records only. It never accepts source code, never scores, and never reports findings. The
calling LLM has the target code in context and does all matching and judgement.

## Consequences

- Fields exist for machine consumption first: `signature` is written to be matched rather than read aloud.
- Eval fixtures remain cheap to derive later, since each entry is self-contained with a known verdict, but no
  effort is spent on them now.
- The server is small enough to be nearly uninteresting, which is the intent — the corpus is the product.
- User code never crosses into the server process.
- Quality of results depends on prompt discipline in the calling model, not on server logic. The usage contract
  is therefore part of the tool descriptions.

## Status

Accepted — 2026-09-04.
