---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: control-flow
tags: [equality, coercion, javascript]
keywords: [" == ", " != ", "== 0", "== \"\"", "== false", "== true"]
signature: "Two values are compared with double equals, so the abstract equality algorithm coerces strings, numbers, booleans and objects into each other before comparing."
distinguish: "Fine for `x == null` and `x != null`, which deliberately match both null and undefined and are allowed by the eqeqeq null option and the Google TypeScript style guide."
added: 2026-09-30
source: ESLint
---

# Loose equality with double equals

## Smell

```typescript
function isSelected(option: { id: number }, selectedId: any): boolean {
  return option.id == selectedId;
}

function isUnset(value: unknown): boolean {
  return value == 0;
}
```

## Why it's bad

- `==` converts operands before comparing: `3 == "03"`, `"" == 0`, `"0" == 0` and `[] == false` are all
  `true`. `isUnset("")` and `isUnset("0")` both return `true`.
- TypeScript only rejects `==` when both static types are known and have no overlap, such as `number == string`.
  Operands typed `any`, `unknown` or a `string | number` union compile without complaint, and those are exactly
  the values that come from forms, query strings and `JSON.parse`.
- It presents as a check that passes in tests with well-typed fixtures and then accepts a string id from the
  URL, or treats an empty text field as zero.

## Better

```typescript
function isSelected(option: { id: number }, selectedId: string): boolean {
  return option.id === Number(selectedId);
}

function isUnset(value: unknown): boolean {
  return value === 0;
}
```
