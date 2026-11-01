---
aliases: [prototype-pollution]
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: mutability
tags: [prototype-pollution, deep-merge, json, javascript]
keywords: ["for (const key in source)", "deepMerge(", "merge(", "target[key] =", "__proto__", "JSON.parse(req.body)"]
signature: "A recursive merge copies every key of a parsed object into a target, so a __proto__ or constructor key walks onto Object.prototype and adds properties to every object in the process."
distinguish: "Fine when the merge skips __proto__, constructor and prototype and copies only own keys, or when the input has already been validated against a schema of known keys."
added: 2026-09-30
source: PortSwigger Web Security Academy
---

# Recursive merge open to prototype pollution

## Smell

```typescript
type Json = { [key: string]: any };

export function deepMerge(target: Json, source: Json): Json {
  for (const key in source) {
    if (typeof source[key] === "object" && source[key] !== null) {
      target[key] = deepMerge(target[key] || {}, source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// deepMerge(userSettings, JSON.parse(req.body));
```

## Why it's bad

- `JSON.parse` treats `"__proto__"` as an ordinary key, so `{"__proto__": {"isAdmin": true}}` arrives as data.
  The merge then reads `target["__proto__"]`, which is `Object.prototype`, and writes `isAdmin` onto it.
- The damage is process-wide and outlives the request: every object that lacks its own `isAdmin` now reads
  `true`, including the ones an authorisation check looks at.
- Blocking `__proto__` alone is not enough; `{"constructor": {"prototype": {...}}}` reaches the same object,
  which is why Node's `--disable-proto` flag does not close the hole either.

## Better

```typescript
type Json = { [key: string]: any };

const UNSAFE_KEYS = new Set(["__proto__", "constructor", "prototype"]);

export function deepMerge(target: Json, source: Json): Json {
  for (const key of Object.keys(source)) {
    if (UNSAFE_KEYS.has(key)) continue;
    const value = source[key];
    const own = Object.prototype.hasOwnProperty.call(target, key);
    if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      target[key] = deepMerge(own ? target[key] : Object.create(null), value);
    } else {
      target[key] = value;
    }
  }
  return target;
}
```
