---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [type-predicates, narrowing, unsoundness, validation]
keywords: [": value is", ": x is", ": obj is", "is User", "\"id\" in", "typeof"]
signature: "A user-defined type predicate returns true after checking one field, and the compiler narrows to the full type on its word, so every unchecked field is trusted without evidence."
distinguish: "Fine when the predicate checks every field the narrowed type promises, or when it discriminates between members of a union already known at the call site, such as testing a kind tag."
added: 2026-09-30
source: Effective TypeScript
---

# Type guard that checks too little

## Smell

```typescript
interface User { id: string; email: string; plan: "free" | "pro" }

function isUser(value: unknown): value is User {
  return typeof value === "object" && value !== null && "id" in value;
}

const body: unknown = await req.json();
if (isUser(body)) {
  sendReceipt(body.email.toLowerCase(), body.plan);
}
```

## Why it's bad

- A type predicate is an assertion in disguise: TypeScript narrows `body` to `User` whenever `isUser` returns
  true and does not check that the body of the guard justifies that. Effective TypeScript lists `is` alongside
  `as` as a source of unsoundness.
- `{ id: "x" }` passes, so `body.email.toLowerCase()` throws even though the line compiles cleanly.
- Fields added to `User` later are never added to the guard, so it drifts further from the type it claims to
  check.

## Better

```typescript
function isUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.id === "string" &&
    typeof v.email === "string" &&
    (v.plan === "free" || v.plan === "pro")
  );
}
```
