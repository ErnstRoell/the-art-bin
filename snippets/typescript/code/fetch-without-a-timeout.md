---
aliases: [unbounded-fetch, fetch-no-abort-signal]
language: typescript
typescript: ">=4.9"
severity: trap
category: correctness
topic: io
tags: [fetch, http, timeout, abort-signal, javascript]
keywords: ["await fetch(", "fetch(url", "signal:", "AbortSignal.timeout", "AbortController"]
signature: "A fetch to a remote service is made without an AbortSignal, and fetch has no timeout option of its own, so a stalled server holds the caller for as long as the platform allows."
distinguish: "Fine when a signal from AbortSignal.timeout, an AbortController or the caller's own signal is passed, or when the HTTP client in use enforces its own timeout."
added: 2026-09-30
source: MDN
---

# Fetch without a timeout

## Smell

```typescript
export async function handler(req: Request): Promise<Response> {
  const quote = await fetch("https://rates.example.com/v1/quote", {
    method: "POST",
    body: await req.text(),
  });
  return new Response(await quote.text(), { status: quote.status });
}
```

## Why it's bad

- `RequestInit` has no `timeout` option; the only way to bound a fetch is its `signal`. Without one, a server
  that accepts the connection and never answers keeps the request open.
- In Node.js the bundled undici client waits up to 300 seconds for response headers by default, so a hung
  dependency holds every incoming request, its memory and its socket for five minutes.
- It works while the dependency is healthy and turns a slow upstream into an outage upstream of it, with
  requests piling up rather than failing fast.

## Better

```typescript
export async function handler(req: Request): Promise<Response> {
  const quote = await fetch("https://rates.example.com/v1/quote", {
    method: "POST",
    body: await req.text(),
    signal: AbortSignal.timeout(5_000),
  });
  return new Response(await quote.text(), { status: quote.status });
}
```

On timeout the fetch rejects with a `DOMException` named `TimeoutError`, which callers can tell apart from an
`AbortError`. `AbortSignal.timeout` is typed in `lib.dom` from TypeScript 4.9.
