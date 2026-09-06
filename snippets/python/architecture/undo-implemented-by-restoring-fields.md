---
aliases: [missing-memento, rollback-by-saving-attributes]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [memento, rollback, snapshot, encapsulation]
keywords: ["old_", "saved_", "= order.total", "except", "order.total =", "rollback"]
signature: "A caller saves an object's state for rollback by copying out the attributes it happens to know about, so a field added later is never restored."
distinguish: "Fine when the saved value is the whole of the state, such as one immutable value swapped back on failure."
added: 2026-09-06
source: refactoring.guru
---

# Undo implemented by restoring fields

## Smell

```python
def apply_discount(order, percent):
    old_total = order.total
    old_lines = order.lines          # the list itself, so the "backup" aliases the original
    old_status = order.status
    try:
        order.recalculate(percent)
        charge(order)
    except PaymentError:
        order.total = old_total
        order.lines = old_lines
        order.status = old_status    # order.coupon, added last quarter, stays discounted
        raise


def retry_shipping(order, carrier):
    old_status = order.status        # a second rollback, restoring a different subset
    try:
        ship(order, carrier)
    except CarrierError:
        order.status = old_status
        raise
```

## Why it's bad

- What "the state of an order" means is decided at the call site, by whoever was reading the class that day.
  Two call sites, two different answers, and neither is wrong in a way a reviewer can see.
- A field added to `Order` is restored by nothing. The rollback silently becomes partial, and the order that
  failed payment keeps its discount — a real inconsistency with no exception attached to it. It surfaces in
  finance reconciliation weeks later, far from the code that caused it.
- `old_lines` is the same list object, so if `recalculate` mutates the list in place rather than replacing it,
  the "restore" writes back the already-modified list and the rollback is a no-op.
- The caller has to read the class's private state to do this at all, so encapsulation is inverted: `Order`
  cannot change its representation without breaking the rollback code in unrelated modules.

## Better

```python
class Order:
    def __init__(self, lines):
        self._state = {"lines": list(lines), "total": 0, "status": "new", "coupon": None}

    def snapshot(self):
        """A memento: opaque to the caller, and complete because the object made it."""
        return deepcopy(self._state)

    def restore(self, snapshot):
        self._state = deepcopy(snapshot)

    def recalculate(self, percent):
        self._state["total"] = sum(line.amount for line in self._state["lines"]) * (1 - percent)


def apply_discount(order, percent):
    saved = order.snapshot()
    try:
        order.recalculate(percent)
        charge(order)
    except PaymentError:
        order.restore(saved)
        raise
```

The class decides what its state is, so a new field is included by construction, the snapshot is a copy rather
than an alias, and both call sites shrink to save-try-restore.
