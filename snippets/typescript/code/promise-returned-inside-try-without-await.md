---
aliases: [return-without-await-in-try, missing-return-await]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: exceptions
tags: [async, promise, try-catch, javascript]
keywords: ["return fetch", "return this.", "try {", "} catch", "return-await"]
signature: "An async function returns a promise from inside a try block without awaiting it, so a rejection settles the returned promise directly and the surrounding catch and finally never see it."
distinguish: "Fine outside any try, catch or finally, where return and return await behave the same apart from stack traces."
added: 2026-09-30
source: typescript-eslint
---

# Promise returned inside try without await

## Smell

```typescript
async function loadConfig(path: string): Promise<Config> {
  try {
    return readJson<Config>(path);
  } catch (err) {
    log.warn("config unreadable, using defaults", err);
    return DEFAULT_CONFIG;
  }
}
```

## Why it's bad

- `return readJson(path)` leaves the `try` block as soon as the promise is created. When that promise later
  rejects, the `catch` has already been passed, so the fallback never runs and the caller gets the rejection.
- The code reads as though a missing file falls back to defaults, and a unit test with a synchronously
  throwing stub will even confirm it; the gap only shows with a real asynchronous failure.
- The same applies to `finally`: cleanup there runs before the returned promise has settled.

## Better

```typescript
async function loadConfig(path: string): Promise<Config> {
  try {
    return await readJson<Config>(path);
  } catch (err) {
    log.warn("config unreadable, using defaults", err);
    return DEFAULT_CONFIG;
  }
}
```
