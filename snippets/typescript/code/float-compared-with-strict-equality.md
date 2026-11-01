---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: numerics
tags: [floating-point, equality, testing, javascript]
keywords: ["=== 1", "=== 0", "!== 0", "=== 0.3", "toBe(0.", "Number.EPSILON"]
signature: "Two numbers that come out of floating point arithmetic are compared with strict equality, so binary representation error decides the answer."
distinguish: "Fine against a value that was assigned rather than computed, such as a sentinel zero, and for integer arithmetic that stays within Number.MAX_SAFE_INTEGER, which doubles represent exactly."
added: 2026-09-30
source: MDN
---

# Float compared with strict equality

## Smell

```typescript
function weightsAreValid(weights: number[]): boolean {
  const total = weights.reduce((sum, w) => sum + w, 0);
  return total === 1;
}

weightsAreValid([0.6, 0.3, 0.1]); // false, total is 0.9999999999999999

test("splits evenly", () => {
  expect(0.3 / 3).toBe(0.1); // fails, 0.09999999999999999
});
```

## Why it's bad

- Decimal fractions such as `0.1` have no exact binary representation, so `0.1 + 0.2 === 0.3` is `false` and
  sums that add up on paper miss by one unit in the last place.
- `Number.EPSILON` is the usual patch and only fits values near magnitude 1. Around 1000 the rounding error is
  about `1e-13`, so `Math.abs(a - b) < Number.EPSILON` fails there too.
- Jest's `toBe` uses `Object.is`, which is exact, so `expect(0.2 + 0.1).toBe(0.3)` fails; the Jest docs
  point to `toBeCloseTo` for floating point results.

## Better

```typescript
function weightsAreValid(weights: number[]): boolean {
  const total = weights.reduce((sum, w) => sum + w, 0);
  return Math.abs(total - 1) < 1e-9; // tolerance chosen for the magnitude of the data
}

test("splits evenly", () => {
  expect(0.3 / 3).toBeCloseTo(0.1);
});
```
