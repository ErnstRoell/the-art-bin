---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: mutability
tags: [spread, shallow-copy, aliasing, javascript, immutability]
keywords: ["{ ...", "{...", "[...", "Object.assign(", ".push(", "structuredClone"]
signature: "An object is copied with spread and then a nested object or array in the copy is mutated, but spread copies only one level, so the original is mutated too."
distinguish: "Fine when only top-level properties of the copy are reassigned, or when each nested level that changes is spread as well, as in the usual immutable-update pattern."
added: 2026-09-30
source: MDN
---

# Object spread mistaken for a deep copy

## Smell

```typescript
interface Config { retries: number; headers: Record<string, string>; tags: string[] }
const defaults: Config = { retries: 3, headers: { accept: "application/json" }, tags: ["api"] };

function withAuth(token: string): Config {
  const config = { ...defaults };
  config.headers.authorization = `Bearer ${token}`;
  config.tags.push("authed");
  return config;
}

withAuth("alice");
withAuth("bob");
```

## Why it's bad

- Spread makes a shallow copy: `config.headers` and `config.tags` are the same objects as in `defaults`, so
  both writes land in `defaults`.
- After two calls, every config built from `defaults` carries `Bearer bob` and two `"authed"` tags, so one
  user's token leaks into another's requests.
- `Object.assign`, `slice`, `concat`, and `Array.from` are shallow in the same way, so swapping one copy idiom
  for another does not fix it; it presents as shared defaults that change "by themselves" between calls.

## Better

```typescript
function withAuth(token: string): Config {
  const config = structuredClone(defaults);
  config.headers.authorization = `Bearer ${token}`;
  config.tags.push("authed");
  return config;
}
```
