---
aliases: [or-default-for-falsy-values]
language: typescript
typescript: ">=3.7"
severity: bug
category: correctness
topic: control-flow
tags: [defaults, falsy, nullish-coalescing, javascript]
keywords: ["|| 0", "|| 1", "|| \"\"", "||=", "opts.", "options."]
signature: "A default is applied with logical or, so a legitimate falsy value such as 0, an empty string or false is replaced by the default as if it were missing."
distinguish: "Fine when every falsy value really should fall back, such as an empty search string meaning no filter, or when the left side is an object type whose only falsy values are null and undefined."
added: 2026-09-30
source: typescript-eslint
---

# Logical or default overrides zero

## Smell

```typescript
interface RetryOptions {
  retries?: number;
  label?: string;
}

function configure(opts: RetryOptions) {
  const retries = opts.retries || 3;
  const label = opts.label || "job";
  return { retries, label };
}

configure({ retries: 0, label: "" }); // { retries: 3, label: "job" }
```

## Why it's bad

- `||` returns its right operand for any falsy left operand, which includes `0`, `""`, `NaN` and `false`, not
  only `null` and `undefined`.
- An optional `number` property is typed `number | undefined`, so the intent is "fall back when absent". A
  caller who asks for zero retries gets three, and one who passes an empty label gets `"job"`.
- It presents as a setting that cannot be turned off: every non-zero value works, and the one that means "none"
  is silently ignored.

## Better

```typescript
function configure(opts: RetryOptions) {
  const retries = opts.retries ?? 3;
  const label = opts.label ?? "job";
  return { retries, label };
}
```
