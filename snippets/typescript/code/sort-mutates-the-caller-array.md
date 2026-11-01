---
aliases: [reverse-mutates-the-caller-array]
language: typescript
typescript: ">=5.2"
severity: trap
category: correctness
topic: mutability
tags: [sorting, arrays, side-effects, aliasing, javascript]
keywords: [".sort(", ".reverse()", "return events.reverse()", "const sorted = values.sort("]
signature: "An array that belongs to the caller or to state is sorted or reversed in place, and because sort and reverse return the same array the mutation reads like a pure transformation."
distinguish: "Fine when the array was created locally, such as the result of a map, filter or spread copy, or when sorting in place is the function's documented purpose and it returns void."
added: 2026-09-30
source: MDN
---

# Sort mutates the caller array

## Smell

```typescript
function median(values: number[]): number {
  const sorted = values.sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function latestFirst(events: AuditEvent[]): AuditEvent[] {
  return events.reverse();
}
```

## Why it's bad

- `sort` and `reverse` reorder the array in place and return a reference to that same array, so `sorted` is
  `values` and the caller's readings are now in a different order.
- Returning the result makes each function look like a pure transformation. Calling `latestFirst` twice on the
  same list flips it back to oldest first.
- In React state the mutation happens behind the setter's back; the React docs call out `sort` and `reverse` as
  mutating and say to copy the array first.
- A `readonly number[]` parameter would have rejected both calls at compile time, since `ReadonlyArray` has no
  `sort` or `reverse`.

## Better

```typescript
function median(values: readonly number[]): number {
  const sorted = values.toSorted((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function latestFirst(events: readonly AuditEvent[]): AuditEvent[] {
  return events.toReversed(); // lib es2023; before TypeScript 5.2 use [...events].reverse()
}
```
