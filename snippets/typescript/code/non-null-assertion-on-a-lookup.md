---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [non-null-assertion, undefined, lookups, unsoundness]
keywords: [".get(", ").get(key)!", ".find(", ")!.", "]!", "!."]
signature: "A lookup that can miss, such as Map.get or Array.find, is followed by a non-null assertion, so the missing case is silenced rather than handled and surfaces later as a TypeError on undefined."
distinguish: "Fine when the preceding line proves presence in a way the compiler cannot follow, such as a has check on the same key immediately before, ideally with a comment saying so."
added: 2026-09-30
source: typescript-eslint
---

# Non-null assertion on a lookup

## Smell

```typescript
const prices = new Map<string, number>();

function lineTotal(sku: string, qty: number): number {
  return prices.get(sku)! * qty;
}

function ownerName(team: Team): string {
  return team.members.find((m) => m.role === "owner")!.name;
}
```

## Why it's bad

- `!` only tells the type checker the value is not `null` or `undefined`; it emits no runtime check. An unknown
  SKU makes `lineTotal` return `NaN`, which then propagates silently into totals.
- `find` on a team with no owner returns `undefined`, and `.name` throws `TypeError` at the use site, with no
  hint of which lookup missed.
- The assertion records an assumption that was true when written, such as every SKU being preloaded, and keeps
  compiling after the assumption stops holding.

## Better

```typescript
function lineTotal(sku: string, qty: number): number {
  const price = prices.get(sku);
  if (price === undefined) throw new Error(`no price for ${sku}`);
  return price * qty;
}

function ownerName(team: Team): string | undefined {
  return team.members.find((m) => m.role === "owner")?.name;
}
```
