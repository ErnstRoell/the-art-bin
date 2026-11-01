---
aliases: [redundant-state-synced-by-effect]
language: typescript
typescript: ">=3.0"
severity: taste
category: performance
topic: functions
tags: [react, hooks, useEffect, derived-state, javascript]
keywords: ["useEffect(", "useState(", "}, [items]);", "setTotal(", "setFiltered(", "setFullName("]
signature: "A useEffect copies a value computed from props or state into another piece of state, so every change renders once with the stale value and again with the new one."
distinguish: "Fine when the effect synchronises with something outside React, such as a subscription, a network request or a browser API, rather than computing a value from props or state."
added: 2026-09-30
source: React docs
---

# Effect used to derive state

## Smell

```typescript
function Cart({ items }: { items: CartItem[] }) {
  const [total, setTotal] = useState(0);
  const [isEmpty, setIsEmpty] = useState(true);

  useEffect(() => {
    setTotal(items.reduce((sum, item) => sum + item.price * item.qty, 0));
    setIsEmpty(items.length === 0);
  }, [items]);

  return isEmpty ? <p>Your cart is empty</p> : <p>Total: {total}</p>;
}
```

## Why it's bad

- React renders with the stale values, commits them to the DOM, runs the effect, and renders again. Here the
  first paint of a full cart says "Your cart is empty".
- `total` and `isEmpty` are extra state that must be kept in step with `items` by hand, and each one is a
  place for the copies to drift apart.
- If the calculation is expensive, the tool is `useMemo`, not an effect; the React docs' "You Might Not Need an
  Effect" covers this case first.

## Better

```typescript
function Cart({ items }: { items: CartItem[] }) {
  const total = items.reduce((sum, item) => sum + item.price * item.qty, 0);
  const isEmpty = items.length === 0;

  return isEmpty ? <p>Your cart is empty</p> : <p>Total: {total}</p>;
}
```
