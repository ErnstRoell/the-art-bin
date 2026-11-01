---
aliases: [global-isnan]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: numerics
tags: [nan, coercion, validation, javascript]
keywords: ["isNaN(", "!isNaN(", "window.isNaN(", "isNaN(req.", "isNaN(body."]
signature: "The global isNaN is used to validate input, but it coerces its argument to a number first, so empty and whitespace strings and booleans become 0 or 1 and pass as numbers."
distinguish: "Fine when the argument is already statically a number, where isNaN and Number.isNaN give the same answer, though Number.isNaN still states the intent."
added: 2026-09-30
source: MDN
---

# Global isNaN coerces its argument

## Smell

```typescript
function readQuantity(quantity: any): number {
  if (isNaN(quantity)) {
    throw new Error("quantity must be a number");
  }
  return quantity;
}

readQuantity("");   // returns "", typed as number
readQuantity(" ");  // returns " "
readQuantity(true); // returns true
```

## Why it's bad

- `isNaN` converts a non-number argument to a number before testing it. `""` and `" "` convert to `0` and
  booleans to `0` or `1`, so none of them is `NaN` and all of them pass validation.
- The value returned is still the original string or boolean, now typed as `number`, and fails later in
  arithmetic or in a database write far from the check.
- `lib.d.ts` declares `isNaN(number: number)`, so TypeScript rejects a `string` argument, but `any` from
  `JSON.parse`, a request body or a form library slips straight through.

## Better

```typescript
function readQuantity(quantity: unknown): number {
  if (typeof quantity !== "number" || Number.isNaN(quantity)) {
    throw new Error("quantity must be a number");
  }
  return quantity;
}
```
