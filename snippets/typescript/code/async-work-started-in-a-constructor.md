---
aliases: [async-constructor]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [async, promises, constructors, floating-promise, javascript]
keywords: ["constructor(", "this.load();", "this.init();", "this.connect();", "void this.", ".then("]
signature: "A constructor starts an async method and drops the promise, so the object is used before it is ready and a failed load becomes an unhandled rejection."
distinguish: "Fine when a static async factory does the loading and the constructor only assigns fields, or when the constructor keeps the promise in a field that every method awaits."
added: 2026-09-30
source: MDN
---

# Async work started in a constructor

## Smell

```typescript
export class ProductCatalog {
  private products: Product[] = [];
  constructor(private readonly url: string) {
    this.load();
  }

  private async load(): Promise<void> {
    const res = await fetch(this.url);
    this.products = await res.json();
  }

  find(id: string): Product | undefined {
    return this.products.find((p) => p.id === id);
  }
}
```

## Why it's bad

- A constructor cannot be `async`, so nothing can await `load()`. `new ProductCatalog(url).find("sku-1")` runs
  before the fetch returns and returns `undefined`, which looks like a missing product rather than a race.
- No one holds the promise, so a failed fetch is an unhandled rejection. Under Node's default
  `--unhandled-rejections=throw` that is raised as an uncaught exception and ends the process.
- typescript-eslint's `no-floating-promises` flags the call, and the caller has no way to wait for readiness,
  surface the error or retry.

## Better

```typescript
export class ProductCatalog {
  private constructor(private readonly products: Product[]) {}

  static async load(url: string): Promise<ProductCatalog> {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`catalog fetch failed: ${res.status}`);
    return new ProductCatalog(await res.json());
  }

  find(id: string): Product | undefined {
    return this.products.find((p) => p.id === id);
  }
}
```
