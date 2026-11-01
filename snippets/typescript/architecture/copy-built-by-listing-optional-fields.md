---
aliases: []
language: typescript
typescript: ">=3.7"
severity: trap
category: correctness
topic: typing
tags: [prototype, copying, optional-properties, spread]
keywords: ["baseUrl: base.baseUrl,", "timeout: base.timeout,", "headers: base.headers", "?: ", "...base", "function withTimeout("]
signature: "A copy of an object is built by listing its properties at the call site, and because the newer properties are optional the compiler accepts a copy that silently drops them."
distinguish: "Fine when the result is deliberately a different, narrower thing built from a few of the original's values rather than a copy of it."
added: 2026-09-30
source: refactoring.guru
---

# Copy built by listing optional fields

## Smell

```typescript
interface RequestConfig {
  baseUrl: string;
  timeout: number;
  retries?: number;
  headers?: Record<string, string>;
  proxy?: string;   // added last month
}

export function forTenant(base: RequestConfig, tenant: string): RequestConfig {
  const headers = base.headers ?? {};
  headers["x-tenant"] = tenant;   // mutates the original's headers
  return {
    baseUrl: base.baseUrl,
    timeout: base.timeout,
    retries: base.retries,
    headers,
  };
}

export function withLongTimeout(base: RequestConfig): RequestConfig {
  return {
    baseUrl: base.baseUrl,
    timeout: 120_000,
    headers: base.headers,
  };
}
```

## Why it's bad

- `proxy` was added after both helpers and is optional, so leaving it out is still a valid `RequestConfig`.
  Both copies quietly drop it, and tenant traffic bypasses the proxy with nothing failing to compile.
- `withLongTimeout` also forgot `retries`, so the config meant to be more patient gives up after the default
  number of attempts, and the omission is indistinguishable from intent.
- `forTenant` writes into `base.headers`, so every later request from the base config carries the last
  tenant's header. Listing fields by hand copies the top level and shares everything nested.
- Each "copy with a change" re-enumerates the type, so the places that must learn about a new field grow with
  every helper.

## Better

```typescript
export function forTenant(base: RequestConfig, tenant: string): RequestConfig {
  return { ...base, headers: { ...base.headers, "x-tenant": tenant } };
}

export function withLongTimeout(base: RequestConfig): RequestConfig {
  return { ...base, timeout: 120_000 };
}
```

Spreading the original carries every property, including the ones added later, and names only what changes.
Nested objects that change are spread too, so the base is never written; reach for `structuredClone` when the
whole value must be deep-copied, and give a class a `clone()` method when it has private state or a prototype
that a spread would lose.
