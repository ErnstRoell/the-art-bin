---
aliases: [fill-with-an-array-literal]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: mutability
tags: [arrays, aliasing, initialisation, javascript]
keywords: [".fill([])", ".fill({})", ".fill(new Array(", ".fill(new Map()", "new Array(n).fill("]
signature: "An array is filled with an object or array value, so every slot references the same single object and a mutation through one index shows up at all of them."
distinguish: "Fine when the fill value is a primitive such as 0, an empty string or null, or when sharing one immutable object across slots is intended."
added: 2026-09-30
source: MDN
---

# Array fill with a shared object

## Smell

```typescript
function emptyBoard(rows: number, cols: number): string[][] {
  return new Array(rows).fill(new Array(cols).fill("."));
}

const board = emptyBoard(3, 3);
board[0][0] = "X"; // every row now starts with "X"

const buckets: number[][] = new Array(10).fill([]);
buckets[3].push(42); // all ten buckets contain 42
```

## Why it's bad

- `fill` puts the exact value it was given into every slot. The argument is evaluated once, so an object or
  array argument means every slot is a reference to that one object.
- The type `string[][]` cannot express that the rows are aliases, so nothing flags it at compile time.
- It presents as a write to one cell or bucket that appears in all of them, often only after the first
  mutation in a test that previously only read the initial values.

## Better

```typescript
function emptyBoard(rows: number, cols: number): string[][] {
  return Array.from({ length: rows }, () => new Array<string>(cols).fill("."));
}

const buckets = Array.from({ length: 10 }, (): number[] => []);
```
