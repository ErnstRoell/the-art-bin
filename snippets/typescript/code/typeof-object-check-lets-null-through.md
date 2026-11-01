---
aliases: [typeof-null-is-object]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: typing
tags: [typeof, null, type-guards, narrowing, javascript]
keywords: ["typeof value === \"object\"", "typeof x === 'object'", "=== \"object\"", "=== 'object'", "value is Record<"]
signature: "A value is tested with typeof equal to object as though that ruled out null, but typeof null is also object, so null passes the check."
distinguish: "Fine when null is excluded in the same condition, such as `typeof x === 'object' && x !== null`, or when the compiler already narrows to `object | null` and rejects the null use under strictNullChecks."
added: 2026-09-30
source: MDN
---

# typeof object check lets null through

## Smell

```typescript
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object";
}

function readId(text: string): unknown {
  const body: unknown = JSON.parse(text);
  if (isRecord(body) && "id" in body) {
    return body.id;
  }
  return undefined;
}
```

## Why it's bad

- `typeof null` is `"object"`, a quirk from the first JavaScript implementation that was never fixed for web
  compatibility. `readId("null")` gets past `isRecord` and throws `TypeError: Cannot use 'in' operator to
  search for 'id' in null`.
- TypeScript narrows an inline `typeof x === "object"` to `object | null`, which catches many misuses. A user
  defined type guard hides that: its body is not checked against the `value is Record<...>` predicate, so the
  compiler trusts it and narrows `null` to a record.
- Arrays also report `"object"`, so `isRecord([1, 2])` is `true` as well.

## Better

```typescript
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
```
