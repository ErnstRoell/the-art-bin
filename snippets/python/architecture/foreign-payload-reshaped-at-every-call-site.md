---
aliases: [missing-adapter, vendor-shape-leaked-inward]
language: python
python: ">=3.0"
severity: trap
category: maintainability
topic: classes
tags: [adapter, boundary, third-party, translation]
keywords: ["[\"data\"]", "_cents", "fromtimestamp", "raw[", "payload[", "response.json()["]
signature: "A foreign API's payload shape is translated into local terms inline wherever it is used, so the translation exists once per call site instead of once per API."
distinguish: "Fine at a single boundary function that already is the one place the foreign shape is translated."
added: 2026-09-06
source: refactoring.guru
---

# Foreign payload reshaped at every call site

## Smell

```python
def sync_orders(client):
    for raw in client.list_orders()["data"]:
        save(
            id=raw["order_id"],
            total=raw["amount_cents"] / 100,
            placed=datetime.fromtimestamp(raw["created_ts"]),
        )


def refund_if_recent(client, order_id):
    raw = client.get_order(order_id)["data"]
    total = raw["amount_cents"] / 100                      # the same three decisions,
    placed = datetime.fromtimestamp(raw["created_ts"])     # retyped, and naive this time
    if total > 0 and placed > cutoff():
        client.refund(raw["order_id"], int(total * 100))


def monthly_total(client, month):
    rows = client.list_orders(month=month)["data"]
    return sum(row["amount_cents"] for row in rows) / 100  # a fourth place that knows about cents
```

## Why it's bad

- Three call sites each hold the vendor's vocabulary: that money arrives in cents, that time arrives as a Unix
  stamp, that everything is wrapped in `data`. The vendor's schema is therefore not a boundary the codebase can
  see; it is spread through the codebase's interior.
- The decisions drift where they are least visible. `refund_if_recent` builds a naive datetime while
  `sync_orders` does too — until one is fixed. Half-fixed timezone handling is exactly the bug shape that
  `naive-datetime-for-instants` describes, and this structure guarantees it happens per site.
- `/ 100` gives a float, so money is now floating point in three places independently. A rounding fix has three
  homes to find, and `grep` for `amount_cents` only finds the ones that spelled it that way.
- When the vendor renames `amount_cents` or nests `data` one level deeper, the change is unbounded — every use
  site is a use of their schema. A test cannot fake the API without reproducing its exact payload shape at
  every call site either.

## Better

```python
@dataclass(frozen=True)
class Order:
    id: str
    total: Decimal
    placed: datetime


class VendorOrders:
    """Adapter: the only code in the repository that knows the vendor's payload shape."""

    def __init__(self, client):
        self._client = client

    def _to_order(self, raw):
        return Order(
            id=raw["order_id"],
            total=Decimal(raw["amount_cents"]) / 100,
            placed=datetime.fromtimestamp(raw["created_ts"], tz=timezone.utc),
        )

    def list(self, month=None):
        return [self._to_order(raw) for raw in self._client.list_orders(month=month)["data"]]

    def get(self, order_id):
        return self._to_order(self._client.get_order(order_id)["data"])

    def refund(self, order):
        self._client.refund(order.id, int(order.total * 100))


def refund_if_recent(orders, order_id):
    order = orders.get(order_id)
    if order.total > 0 and order.placed > cutoff():
        orders.refund(order)
```

Cents, epochs and the `data` envelope now appear once each. The rest of the program is written in `Order`, and
a test hands `refund_if_recent` an adapter double with no payloads in it at all.
