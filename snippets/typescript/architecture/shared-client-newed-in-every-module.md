---
aliases: []
language: typescript
typescript: ">=3.7"
severity: trap
category: correctness
topic: classes
tags: [singleton, shared-state, modules, composition-root]
keywords: ["new FeatureFlags(", "new PrismaClient()", "new Pool(", "new ApiClient(", "await flags.load()", "export async function"]
signature: "A class holding shared state or an expensive resource is constructed with new inside each function or module that needs it, so the instances disagree with each other and the setup cost is paid per call site."
distinguish: "Fine when the class is a cheap value whose instances hold nothing that needs sharing, or when a fresh instance per request or per test is the point."
added: 2026-09-30
source: refactoring.guru
---

# Shared client newed in every module

## Smell

```typescript
// flags.ts
export class FeatureFlags {
  private flags: Record<string, boolean> = {};
  private overrides: Record<string, boolean> = {};
  async load() { this.flags = await (await fetch(FLAGS_URL)).json(); }
  enabled(name: string) { return this.overrides[name] ?? this.flags[name] ?? false; }
  override(name: string, value: boolean) { this.overrides[name] = value; }
}

// checkout.ts
export async function checkout(cart: Cart) {
  const flags = new FeatureFlags();
  await flags.load();                               // one HTTP request per checkout
  const db = new PrismaClient();                    // a new connection pool per checkout
  const price = flags.enabled("newPricing") ? newPrice(cart) : oldPrice(cart);
  return db.order.create({ data: { cartId: cart.id, price } });
}

// banner.ts
export async function banner() {
  const flags = new FeatureFlags();
  await flags.load();
  return flags.enabled("newPricing") ? "new" : "old";   // may disagree with checkout
}
```

## Why it's bad

- `FeatureFlags` holds overrides, and overrides only mean anything if everyone reads the same instance. Each
  function has its own, so `override` affects nobody and a test that sets one watches the code ignore it.
- Two instances loaded either side of a flag flip give two answers in the same request, so the page renders
  half new and half old.
- `new PrismaClient()` per call opens a new connection pool every time, so under load the service exhausts the
  database's connection limit while each pool sits nearly empty.
- The usual over-correction is a class with a private constructor and a static `getInstance()`, which is a
  global with extra steps and just as hard to replace in a test.

## Better

```typescript
// clients.ts: evaluated once per process, so these are the only instances
export const flags = new FeatureFlags();
export const db = new PrismaClient();
export const ready = flags.load();

// checkout.ts
export async function checkout(cart: Cart, deps = { flags, db }) {
  await ready;
  const price = deps.flags.enabled("newPricing") ? newPrice(cart) : oldPrice(cart);
  return deps.db.order.create({ data: { cartId: cart.id, price } });
}
```

An ES module is evaluated once, so a module-level instance already is the single shared one, without any
`getInstance` machinery. Taking it as a defaulted parameter keeps it replaceable in tests; state that must be
per request or per user belongs in a value built per request instead.
