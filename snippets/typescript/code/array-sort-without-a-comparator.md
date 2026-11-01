---
aliases: [numbers-sorted-as-strings]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: stdlib-misuse
tags: [sorting, arrays, comparators, javascript]
keywords: [".sort()", ".toSorted()", "].sort()", ".sort().reverse()"]
signature: "An array of numbers or other non-strings is sorted without a compare function, so elements are converted to strings and ordered by UTF-16 code units."
distinguish: "Fine on an array of strings where code unit order is acceptable, which is why require-array-sort-compare ignores string arrays by default, though text shown to people usually wants localeCompare."
added: 2026-09-30
source: typescript-eslint
---

# Array sort without a comparator

## Smell

```typescript
function topScores(scores: number[]): number[] {
  return [...scores].sort().reverse().slice(0, 3);
}

topScores([9, 80, 100, 7]); // [9, 80, 7]
```

## Why it's bad

- With no compare function, `sort` converts every element to a string and compares code units, so `100` sorts
  before `7` and `[1, 30, 4, 21, 100000]` becomes `[1, 100000, 21, 30, 4]`.
- `number[]` has a perfectly typed `sort()`, so the compiler cannot help; the result has the right type and the
  wrong order.
- It passes every test whose values have the same number of digits, and breaks the first time a score reaches
  three digits.

## Better

```typescript
function topScores(scores: number[]): number[] {
  return [...scores].sort((a, b) => b - a).slice(0, 3);
}
```
