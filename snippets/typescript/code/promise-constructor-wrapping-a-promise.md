---
aliases: [explicit-promise-construction, deferred-antipattern]
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: concurrency
tags: [promise, async, antipattern, javascript]
keywords: ["new Promise(", "(resolve, reject) =>", ".then(resolve", ".catch(reject", "resolve(await"]
signature: "A new Promise is constructed only to forward the result of an API that already returns a promise, so the wrapper adds resolve and reject plumbing that can silently drop errors."
distinguish: "Fine when wrapping a callback or event API that has no promise form, which is what the Promise constructor is for."
added: 2026-09-30
source: MDN
---

# Promise constructor wrapping a promise

## Smell

```typescript
function getUserName(id: string): Promise<string> {
  return new Promise((resolve, reject) => {
    fetchUser(id)
      .then((user) => resolve(user.name))
      .catch(reject);
  });
}
```

## Why it's bad

- MDN describes the `Promise()` constructor as primarily for wrapping callback-based APIs, and notes that a
  task which is already promise-based likely does not need it. Here the constructor only relays `fetchUser`.
- The relay has to be written correctly by hand every time. Forget the `.catch(reject)` and a failure leaves
  the outer promise pending forever while the inner rejection goes unhandled; Bluebird's anti-pattern guide
  warns that this superfluous wrapping swallows errors.
- It is three layers of nesting for what is one transformation of an existing promise.

## Better

```typescript
async function getUserName(id: string): Promise<string> {
  const user = await fetchUser(id);
  return user.name;
}
```
