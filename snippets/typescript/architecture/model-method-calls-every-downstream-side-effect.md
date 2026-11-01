---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [observer, events, coupling, notifications]
keywords: ["await sendReceipt(", "await reserveStock(", "warehouse.notify(", "metrics.increment(", "this.status = \"paid\"", "async pay("]
signature: "The object that changed calls each interested subsystem by name, so it depends on every consumer of its own event."
distinguish: "Fine when the call is part of the operation rather than a notification about it, such as saving the row the operation exists to write."
added: 2026-09-30
source: refactoring.guru
---

# Model method calls every downstream side effect

## Smell

```typescript
export class Order {
  status: "open" | "paid" | "refunded" = "open";

  async pay(payment: Payment): Promise<void> {
    await gateway.capture(payment);
    this.status = "paid";
    await db.orders.save(this);
    await sendReceipt(this);             // the order now imports email,
    await reserveStock(this.lines);      // inventory,
    await warehouse.notify(this.id);     // the warehouse,
    metrics.increment("order.paid");     // metrics,
    if (this.total > 10_000) {
      await fraudTeam.review(this);      // and another team's escalation policy
    }
  }

  async refund(): Promise<void> {
    await gateway.refund(this.paymentId);
    this.status = "refunded";
    await db.orders.save(this);
    await sendRefundNotice(this);
    await releaseStock(this.lines);      // the warehouse is never told, so it ships anyway
    metrics.increment("order.refunded");
  }
}
```

## Why it's bad

- `Order` is a model of an order and holds knowledge of five subsystems. Its import list is the union of
  everything anyone wanted to happen after a payment, and it grows every quarter.
- Each consumer's failure becomes the payment's failure. If `warehouse.notify` rejects, the card is captured and
  the order saved, but `pay` rejects too, so the caller retries a payment that succeeded.
- `pay` and `refund` each keep their own list, and nothing forces them to agree: the warehouse hears about
  payments and not about refunds.
- The fraud threshold sits inside `pay`, so another team's policy is changed by editing the order model, and a
  test of `pay` begins with five `jest.mock` calls before its one assertion.

## Better

```typescript
type OrderEvents = { paid: Order; refunded: Order };

export class Emitter<E> {
  private readonly handlers: { [K in keyof E]?: Array<(payload: E[K]) => unknown> } = {};

  on<K extends keyof E>(name: K, handler: (payload: E[K]) => unknown): () => void {
    const list = this.handlers[name] || (this.handlers[name] = []);
    list.push(handler);
    return () => {
      const i = list.indexOf(handler);
      if (i >= 0) list.splice(i, 1);
    };
  }

  emit<K extends keyof E>(name: K, payload: E[K]): void {
    for (const handler of (this.handlers[name] || []).slice()) {
      const report = (err: unknown) => log.error(`${String(name)} handler failed`, err);
      try {
        Promise.resolve(handler(payload)).catch(report);
      } catch (err) {
        report(err);
      }
    }
  }
}

export class Order {
  constructor(private readonly events: Emitter<OrderEvents>) {}

  async pay(payment: Payment): Promise<void> {
    await gateway.capture(payment);
    this.status = "paid";
    await db.orders.save(this);
    this.events.emit("paid", this);      // states what happened, not who cares
  }
}

// Subscribed once, where the process is assembled:
orderEvents.on("paid", sendReceipt);
orderEvents.on("paid", (order) => warehouse.notify(order.id));
orderEvents.on("refunded", (order) => warehouse.cancel(order.id));
```

`Order` depends only on the emitter, a new consumer is a subscription rather than an edit to the model, the
event map keeps names and payloads type-checked, and one failing subscriber no longer fails a payment that went
through. `EventTarget` or Node's `EventEmitter` can do the delivery if their error handling suits.
