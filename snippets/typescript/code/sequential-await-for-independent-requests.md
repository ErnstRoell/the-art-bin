---
aliases: [await-in-loop, serial-awaits]
language: typescript
typescript: ">=3.0"
severity: taste
category: performance
topic: concurrency
tags: [async, promise, latency, javascript]
keywords: ["for (const", "await", "no-await-in-loop", "Promise.all"]
signature: "Independent async requests are awaited one after another, in a loop or in consecutive statements, so total latency is the sum of every round trip instead of the slowest one."
distinguish: "Fine when each step needs the previous result, when running them together would exhaust a bounded resource or a rate limit, or when the order of side effects matters."
added: 2026-09-30
source: ESLint
---

# Sequential await for independent requests

## Smell

```typescript
async function loadDashboard(userId: string): Promise<Dashboard> {
  const profile = await api.getProfile(userId);
  const orders = await api.getOrders(userId);
  const alerts = await api.getAlerts(userId);

  const prices: Price[] = [];
  for (const order of orders) {
    prices.push(await api.getPrice(order.sku));
  }
  return { profile, orders, alerts, prices };
}
```

## Why it's bad

- None of these requests depends on another's result, but each `await` holds back the next request until the
  previous one has come back, so the page waits for three plus N round trips in a row.
- ESLint's `no-await-in-loop` exists for exactly this: each successive operation does not start until the
  previous one has completed, which gives up the parallelism async code is for.
- MDN's promise guide makes the same point: before composing promises sequentially, consider whether it is
  necessary, because running them concurrently avoids blocking each other.

## Better

```typescript
async function loadDashboard(userId: string): Promise<Dashboard> {
  const [profile, orders, alerts] = await Promise.all([
    api.getProfile(userId),
    api.getOrders(userId),
    api.getAlerts(userId),
  ]);
  const prices = await Promise.all(orders.map((order) => api.getPrice(order.sku)));
  return { profile, orders, alerts, prices };
}
```

`Promise.all` rejects on the first failure; use `Promise.allSettled` when every result is wanted regardless.
