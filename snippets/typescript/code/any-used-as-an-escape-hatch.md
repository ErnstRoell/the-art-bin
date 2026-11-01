---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: maintainability
topic: typing
tags: [any, unknown, type-safety, unsoundness]
keywords: [": any", "as any", "<any>", "any[]", "Record<string, any>"]
signature: "A value is typed any to make an error go away, so every property access, call, and assignment through it is unchecked and the any flows on into whatever it touches."
distinguish: "Fine when the value is typed unknown and narrowed before use, or when a single any is confined inside a small helper whose own signature is precise."
added: 2026-09-30
source: typescript-eslint
---

# any used as an escape hatch

## Smell

```typescript
function totalPrice(order: any): number {
  return order.items.reduce((sum: number, item: any) => sum + item.price * item.qty, 0);
}

const order: any = await loadOrder(id);
const total: number = totalPrice(order);
const label: string = order.customer.name.toUpperCase();
```

## Why it's bad

- `any` turns off checking for the value: the handbook's own example shows `obj.foo()`, `obj()`, and
  `const n: number = obj` all compiling on an `any`. A renamed field such as `quantity` for `qty` is not an
  error here; it is `NaN` at runtime.
- It spreads silently. `order.customer.name` is also `any`, and so is anything derived from it, so the unchecked
  region grows past the line where the `any` was written.
- Refactoring tools and editor completion have nothing to go on, so renames skip these sites and reviewers
  cannot see what shape the code expects.

## Better

```typescript
interface OrderItem { price: number; qty: number }
interface Order { items: OrderItem[]; customer: { name: string } }

function totalPrice(order: Order): number {
  return order.items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

const raw: unknown = await loadOrder(id);
if (!isOrder(raw)) throw new Error("malformed order");
const total = totalPrice(raw);
```
