---
aliases: [async-foreach, await-inside-foreach]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: concurrency
tags: [async, promise, array, javascript]
keywords: [".forEach(async", "forEach(async (", "await", "no-misused-promises"]
signature: "An async function is passed to Array.prototype.forEach, which ignores the promise each call returns, so the code after the loop runs before any iteration finishes and their rejections are unhandled."
distinguish: "Fine with for...of and await for sequential work, or with map to promises and Promise.all for concurrent work, where the caller actually waits."
added: 2026-09-30
source: MDN
---

# Async callback passed to forEach

## Smell

```typescript
async function importUsers(rows: Row[]): Promise<number> {
  let imported = 0;
  rows.forEach(async (row) => {
    await db.insert(toUser(row));
    imported += 1;
  });
  return imported;
}
```

## Why it's bad

- MDN is explicit: `forEach()` expects a synchronous function and does not wait for promises. It calls the
  callback for every row, discards each returned promise and returns immediately.
- `importUsers` therefore resolves to `0`, before a single insert has finished, and whatever runs next sees a
  partly populated table.
- A failed insert rejects a promise nobody holds, so the error surfaces as an unhandled rejection instead of
  failing `importUsers`. The `await` inside the callback makes the code look sequential when it is not.

## Better

```typescript
async function importUsers(rows: Row[]): Promise<number> {
  let imported = 0;
  for (const row of rows) {
    await db.insert(toUser(row));
    imported += 1;
  }
  return imported;
}
```

When the inserts are independent, `await Promise.all(rows.map((row) => db.insert(toUser(row))))` runs them
concurrently and still waits for all of them.
