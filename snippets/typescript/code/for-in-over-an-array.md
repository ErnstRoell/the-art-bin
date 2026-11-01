---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: control-flow
tags: [loops, arrays, iteration, javascript]
keywords: ["for (const i in ", "for (let i in ", "for (var i in ", "for (const key in items"]
signature: "An array is iterated with for-in, which visits enumerable property names as strings, including inherited ones, rather than the array's elements."
distinguish: "Fine over a plain object used as a dictionary, ideally guarded with Object.hasOwn or replaced by Object.entries, since for-in is designed for object keys rather than array positions."
added: 2026-09-30
source: MDN
---

# for-in over an array

## Smell

```typescript
function total(prices: number[]): number {
  let sum = 0;
  for (const i in prices) {
    sum += prices[i];
  }
  return sum;
}
```

## Why it's bad

- `for...in` walks every enumerable property, including ones inherited through the prototype chain. A
  polyfill or library that adds an enumerable method to `Array.prototype` gets visited too, and `sum` becomes
  the string `"3function(){}"`.
- The keys are strings, not numbers. TypeScript types `i` as `string` and still allows `prices[i]`, so index
  arithmetic compiles and goes wrong: `` `row ${i + 1}` `` prints `row 01`, `row 11`.
- It works in a clean test environment and breaks when the page loads a script that extends built-ins.

## Better

```typescript
function total(prices: number[]): number {
  let sum = 0;
  for (const price of prices) {
    sum += price;
  }
  return sum;
}
```
