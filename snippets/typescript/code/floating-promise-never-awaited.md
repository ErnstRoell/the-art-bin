---
aliases: [unhandled-promise, fire-and-forget-promise]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: concurrency
tags: [async, promise, unhandled-rejection, javascript]
keywords: ["async function", "save(", "send(", "no-floating-promises", "UnhandledPromiseRejection"]
signature: "A call that returns a promise is used as a bare statement with no await, return or rejection handler, so the caller moves on before it settles and a rejection goes nowhere."
distinguish: "Fine when the promise is awaited, returned, passed to Promise.all or given a catch handler, or when a deliberate fire-and-forget is marked with void and the called function handles its own errors."
added: 2026-09-30
source: typescript-eslint
---

# Floating promise never awaited

## Smell

```typescript
async function checkout(cart: Cart, db: Db): Promise<Receipt> {
  const receipt = buildReceipt(cart);
  db.saveOrder(receipt);
  mailer.sendConfirmation(cart.email, receipt);
  return receipt;
}
```

## Why it's bad

- `checkout` resolves before the order is written, so a caller that reads the order back straight away can
  miss it; typescript-eslint calls this out as improperly sequenced operations.
- If `saveOrder` rejects, nothing observes the rejection: the customer gets a receipt for an order that was
  never stored, and `checkout`'s own caller has no way to find out.
- Since Node.js 15 the default `--unhandled-rejections=throw` raises an unhandled rejection as an uncaught
  exception, so the lost error can also crash the process, away from any stack frame that could handle it.

## Better

```typescript
async function checkout(cart: Cart, db: Db): Promise<Receipt> {
  const receipt = buildReceipt(cart);
  await db.saveOrder(receipt);
  // The confirmation email is best-effort and must not fail the checkout.
  void mailer.sendConfirmation(cart.email, receipt).catch((err) => log.warn("confirmation failed", err));
  return receipt;
}
```
