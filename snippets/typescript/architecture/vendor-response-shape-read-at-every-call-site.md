---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: maintainability
topic: classes
tags: [adapter, boundary, third-party, translation]
keywords: ["res.data.", "amount_cents / 100", "* 1000)", "as any", "Stripe.Charge", ".json() as"]
signature: "A foreign API's response shape is translated into local terms inline wherever it is used, so the translation exists once per call site instead of once per API."
distinguish: "Fine when a single boundary function already is the one place the foreign shape is translated, or when the foreign type is used in exactly one place."
added: 2026-09-30
source: refactoring.guru
---

# Vendor response shape read at every call site

## Smell

```typescript
export async function syncOrders(): Promise<void> {
  const res = await (await fetch(`${VENDOR}/orders`)).json();
  for (const raw of res.data) {
    await db.upsertOrder({
      id: raw.order_id,
      total: raw.amount_cents / 100,
      placedAt: new Date(raw.created * 1000),
    });
  }
}

export async function refundIfRecent(orderId: string): Promise<void> {
  const raw = (await (await fetch(`${VENDOR}/orders/${orderId}`)).json()).data;
  const ageMs = Date.now() - raw.created;                 // seconds, compared as milliseconds
  if (ageMs < 30 * DAY_MS) await refund(orderId, raw.amount_cents);   // cents, not dollars
}

export function orderSummary(raw: any): string {
  return `${raw.order_id}: $${(raw.amount / 100).toFixed(2)}`;   // "amount" is undefined
}
```

## Why it's bad

- Every call site holds the vendor's vocabulary: money in cents, time as Unix seconds, everything wrapped in
  `data`. The vendor's schema is not a boundary; it is spread through the interior of the codebase.
- The decisions have already diverged. `refundIfRecent` compares seconds with milliseconds and passes cents
  where dollars are expected, and `orderSummary` reads a field that does not exist, all as `any`, so the
  compiler checks none of it.
- When the vendor renames `amount_cents` or nests `data` deeper, every use site changes, and a test cannot fake
  the API without reproducing its exact payload shape at each of them.

## Better

```typescript
interface VendorOrder {   // the vendor's shape, named once
  order_id: string;
  amount_cents: number;
  created: number;        // Unix seconds
}

export interface Order {  // ours
  id: string;
  total: number;
  placedAt: Date;
}

function toOrder(raw: VendorOrder): Order {
  return { id: raw.order_id, total: raw.amount_cents / 100, placedAt: new Date(raw.created * 1000) };
}

export const vendor = {
  async orders(): Promise<Order[]> {
    const body: { data: VendorOrder[] } = await (await fetch(`${VENDOR}/orders`)).json();
    return body.data.map(toOrder);
  },
  async order(id: string): Promise<Order> {
    const body: { data: VendorOrder } = await (await fetch(`${VENDOR}/orders/${id}`)).json();
    return toOrder(body.data);
  },
};
```

The translation happens once, at the edge, and everything past it speaks in `Order`. Parsing the body with a
runtime schema such as zod at the same spot also rejects payloads that do not match, rather than trusting the
annotation.
