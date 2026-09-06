---
aliases: [missing-observer, notifications-hardcoded-in-the-subject]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [observer, events, coupling, notifications]
keywords: ["send_email(", "update_inventory(", "record_metric(", "notify_", "self.status =", "def pay(self)"]
signature: "The object that changed calls each interested subsystem by name, so it depends on every consumer of its own event."
distinguish: "Fine when the call is part of the operation rather than a notification about it, such as writing the row the operation exists to write."
added: 2026-09-06
source: refactoring.guru
---

# Subject calls its listeners by name

## Smell

```python
class Order:
    def pay(self, payment):
        self.status = "paid"
        self.paid_at = now()
        save(self)
        email_customer(self)         # the order now imports email,
        update_inventory(self)       # inventory,
        notify_warehouse(self)       # the warehouse,
        record_metric("order.paid")  # metrics,
        if self.total > 10_000:
            alert_fraud_team(self)   # and the fraud team's escalation policy
```

## Why it's bad

- `Order` is a model of an order and holds knowledge of five subsystems. Its import list is the union of
  everything anyone ever wanted to happen after a payment, and it grows every quarter.
- Every consumer's failure becomes the payment's failure. If `notify_warehouse` raises, the order is paid and
  saved but `pay` propagates an exception, so the caller sees a failed payment that actually succeeded.
- The fraud threshold sits inside `pay`, so a policy owned by another team is changed by editing the order
  model, and the tests for that policy have to pay for an order.
- Testing `pay` requires stubbing five modules, which is what makes this recognisable in the wild: a test file
  with a stack of patches at the top and one assertion at the bottom.
- Reversing the direction is the entire fix. The alternative shape — every subsystem polling for orders that
  became paid — trades this coupling for `sleep-to-await-a-condition`, so it is not an improvement.

## Better

```python
class Order:
    def __init__(self, events):
        self._events = events

    def pay(self, payment):
        self.status = "paid"
        self.paid_at = now()
        save(self)
        self._events.emit("order.paid", self)   # states what happened, not who cares


class Events:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, name, handler):
        self._subscribers[name].append(handler)

    def emit(self, name, payload):
        for handler in self._subscribers[name]:
            try:
                handler(payload)
            except Exception:
                log.exception("subscriber %r failed for %s", handler, name)


# Subscribed once, where the process is assembled:
#     events.subscribe("order.paid", email_customer)
#     events.subscribe("order.paid", update_inventory)
#     events.subscribe("order.paid", fraud_check)
```

`Order` depends on nothing but the event bus, a new consumer is a subscription rather than an edit to the model,
and one broken subscriber no longer fails a payment that went through.
