---
aliases: [fetch-ignores-http-status, unchecked-response-ok]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: io
tags: [fetch, http, error-handling, javascript]
keywords: ["await fetch(", "fetch(url)", ".json()", "res.json()", "response.ok", "res.ok"]
signature: "The result of fetch is parsed and used without checking ok or status, because fetch resolves normally for 4xx and 5xx responses and only rejects on network failure."
distinguish: "Fine when response.ok or response.status is checked before the body is used, or when the call goes through a wrapper that already throws on error statuses."
added: 2026-09-30
source: MDN
---

# Fetch response used without checking ok

## Smell

```typescript
async function getAccount(id: string): Promise<Account> {
  const res = await fetch(`/api/accounts/${id}`);
  return (await res.json()) as Account;
}
```

## Why it's bad

- MDN: a `fetch()` promise only rejects when the request fails, such as a network error; it does not reject on
  HTTP error statuses like `404` or `504`. The `try`/`catch` a caller wraps around this never sees a 500.
- On an error status the body is whatever the server sent: an error JSON that gets cast to `Account` and
  flows on with `undefined` fields, or an HTML error page that makes `res.json()` throw a `SyntaxError` far
  from the real cause.
- The cast hides it from the type checker, so the first visible failure is a blank field or a crash somewhere
  downstream.

## Better

```typescript
async function getAccount(id: string): Promise<Account> {
  const res = await fetch(`/api/accounts/${id}`);
  if (!res.ok) {
    throw new Error(`GET /api/accounts/${id} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as Account;
}
```
