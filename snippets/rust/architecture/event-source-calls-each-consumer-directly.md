---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [observer, events, channels, coupling]
keywords: ["email::send_receipt(", "inventory::reserve(", "metrics::increment(", "warehouse::notify(", "fn pay(&mut self", "broadcast::Sender"]
signature: "The value that changed calls each interested subsystem by name, so it depends on every consumer of its own event."
distinguish: "Fine when the call is part of the operation rather than a notification about it, such as writing the row the operation exists to write."
added: 2026-09-23
source: refactoring.guru
---

# Event source calls each consumer directly

## Smell

```rust
impl Order {
    pub async fn pay(&mut self, deps: &Deps) -> Result<(), PayError> {
        self.status = Status::Paid;
        self.paid_at = Some(Utc::now());
        deps.db.save_order(self).await?;
        email::send_receipt(&deps.mailer, self).await?;       // the order knows about email,
        inventory::reserve(&deps.inventory, &self.lines).await?; // inventory,
        warehouse::notify(&deps.warehouse, self.id).await?;   // the warehouse,
        metrics::increment("order.paid");                     // metrics,
        if self.total > Money::from_major(10_000) {
            fraud::escalate(&deps.fraud, self).await?;        // and the fraud team's threshold
        }
        Ok(())
    }
}
```

## Why it's bad

- `Order` is a domain type that now depends on five subsystems, and `Deps` grows a field every time another
  team wants to hear about payments.
- Every consumer's failure becomes the payment's failure. If the warehouse call errors, the order is paid and
  saved but `pay` returns `Err`, so the caller reports a failed payment that went through.
- The fraud threshold lives inside `pay`, so a policy owned by another team changes by editing the order type.
- Testing `pay` needs fakes for every subsystem, which is how this is recognised in the wild: a test that
  builds a large `Deps` in order to assert one status.

## Better

```rust
#[derive(Clone)]
pub enum OrderEvent {
    Paid { order_id: OrderId, total: Money },
}

impl Order {
    pub async fn pay(&mut self, db: &Db, events: &broadcast::Sender<OrderEvent>) -> Result<(), PayError> {
        self.status = Status::Paid;
        self.paid_at = Some(Utc::now());
        db.save_order(self).await?;
        let _ = events.send(OrderEvent::Paid { order_id: self.id, total: self.total }); // no subscribers is fine
        Ok(())
    }
}

// Each consumer subscribes where the process is assembled, and runs in its own task:
// tokio::spawn(email::on_order_events(events.subscribe(), mailer));
// tokio::spawn(fraud::on_order_events(events.subscribe(), fraud_client));
```

`Order` depends on the channel alone, a new consumer is a subscription rather than an edit, and one failing
consumer no longer fails a payment that succeeded.
