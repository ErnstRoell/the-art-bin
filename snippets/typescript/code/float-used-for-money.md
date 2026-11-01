---
aliases: [currency-as-floating-point]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: numerics
tags: [money, floating-point, rounding, javascript]
keywords: ["price: number", "amount: number", ".toFixed(2)", "parseFloat(", "* (1 + taxRate)", "total: number"]
signature: "Currency amounts are held as fractional numbers in major units, so binary floating point error accumulates across sums and tax and toFixed rounds the binary value rather than the decimal one."
distinguish: "Fine for display-only estimates, analytics and charts where cent-level error is acceptable, or when amounts are integer minor units that stay within Number.MAX_SAFE_INTEGER."
added: 2026-09-30
source: The Floating-Point Guide
---

# Float used for money

## Smell

```typescript
interface LineItem {
  price: number; // dollars, such as 19.99
  qty: number;
}

function invoiceTotal(items: LineItem[], taxRate: number): number {
  const subtotal = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  return subtotal * (1 + taxRate);
}

const label = `$${invoiceTotal(cart, 0.08).toFixed(2)}`;
```

## Why it's bad

- Amounts like `0.10` and `0.20` are not exactly representable, so `0.1 + 0.2` is `0.30000000000000004` and a
  large invoice drifts away from the sum of its lines.
- `toFixed` rounds the stored binary value, not the decimal that was typed: `(2.55).toFixed(1)` is `"2.5"`
  because the nearest double is just below 2.55. Half-cent results round in whichever direction the error falls.
- The guidance from the Floating-Point Guide is direct: when results have to add up exactly, especially with
  money, use a decimal type or do the arithmetic in integer cents.

## Better

```typescript
interface LineItem {
  priceCents: number; // integer minor units; use bigint past Number.MAX_SAFE_INTEGER
  qty: number;
}

function invoiceTotalCents(items: LineItem[], taxBasisPoints: number): number {
  const subtotal = items.reduce((sum, i) => sum + i.priceCents * i.qty, 0);
  return subtotal + Math.round((subtotal * taxBasisPoints) / 10_000);
}

const usd = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const label = usd.format(invoiceTotalCents(cart, 800) / 100);
```
