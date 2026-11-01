---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [memento, rollback, snapshot, immutability]
keywords: ["const oldTotal =", "const oldStatus =", "order.total = oldTotal", "catch (err)", "throw err;", "order.lines = "]
signature: "A caller saves an object's state for rollback by copying out the properties it happens to know about, so a property added later is never restored."
distinguish: "Fine when the saved value is the whole of the state, such as one immutable object reference swapped back on failure."
added: 2026-09-30
source: refactoring.guru
---

# Rollback by copying properties back by hand

## Smell

```typescript
export async function applyDiscount(order: Order, percent: number): Promise<void> {
  const oldTotal = order.total;
  const oldLines = order.lines;        // the same array, so the "backup" aliases the original
  const oldStatus = order.status;
  try {
    order.recalculate(percent);
    await charge(order);
  } catch (err) {
    order.total = oldTotal;
    order.lines = oldLines;
    order.status = oldStatus;          // order.coupon, added last quarter, stays applied
    throw err;
  }
}

export async function retryShipping(order: Order, carrier: Carrier): Promise<void> {
  const oldStatus = order.status;      // a second rollback, restoring a different subset
  try {
    await ship(order, carrier);
  } catch (err) {
    order.status = oldStatus;
    throw err;
  }
}
```

## Why it's bad

- What "the state of an order" means is decided at each call site, by whoever read the class that day. Two
  call sites give two answers, and neither is wrong in a way a reviewer can see.
- A property added to `Order` is restored by nothing. The rollback silently becomes partial, and an order that
  failed payment keeps its coupon, an inconsistency with no exception attached that surfaces weeks later in
  reconciliation.
- `oldLines` is the same array, so if `recalculate` edits lines in place rather than replacing the array, the
  restore writes back the already-modified array and the rollback does nothing.
- The caller must reach into the order's state to do this at all, so `Order` cannot change its representation
  without breaking rollback code in unrelated modules.

## Better

```typescript
interface OrderState {
  readonly lines: ReadonlyArray<Line>;
  readonly total: number;
  readonly status: "new" | "charged" | "shipped";
  readonly coupon?: string;
}

export class Order {
  private state: OrderState;

  constructor(lines: Line[]) {
    this.state = { lines: [...lines], total: 0, status: "new" };
  }

  /** A memento: complete because the object made it, and safe because state is never mutated. */
  snapshot(): Readonly<OrderState> {
    return this.state;
  }

  restore(saved: Readonly<OrderState>): void {
    this.state = saved;
  }

  recalculate(percent: number): void {
    const gross = this.state.lines.reduce((sum, line) => sum + line.amount, 0);
    this.state = { ...this.state, total: gross * (1 - percent) };
  }
}

export async function applyDiscount(order: Order, percent: number): Promise<void> {
  const saved = order.snapshot();
  try {
    order.recalculate(percent);
    await charge(order);
  } catch (err) {
    order.restore(saved);
    throw err;
  }
}
```

Because every change replaces the state object instead of editing it, the snapshot is one reference that
already includes any property added later, and both call sites shrink to save, try, restore. When state has to
be mutated in place, `snapshot` returns `structuredClone(this.state)` instead.
