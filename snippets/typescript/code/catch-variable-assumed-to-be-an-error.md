---
aliases: [catch-err-any, unchecked-catch-binding]
language: typescript
typescript: ">=4.4"
severity: trap
category: correctness
topic: exceptions
tags: [error-handling, unknown, narrowing, strict]
keywords: ["catch (err)", "catch (e: any)", "err.message", "e.message", "as Error", "useUnknownInCatchVariables"]
signature: "A catch block reads properties such as message or code off the caught value without narrowing it, although JavaScript lets any value be thrown."
distinguish: "Fine when the value is narrowed first with instanceof Error or a type guard, or when it is only passed on unexamined to a logger or rethrown."
added: 2026-09-30
source: TypeScript 4.4 release notes
---

# Catch variable assumed to be an Error

## Smell

```typescript
try {
  await payments.charge(order);
} catch (err: any) {
  if (err.code === "card_declined") {
    return { status: "declined", reason: err.message };
  }
  throw err;
}
```

## Why it's bad

- A catch binding holds whatever value was thrown, and JavaScript allows throwing strings, `undefined` or
  plain objects. If a dependency throws `undefined`, `err.code` itself throws a `TypeError` inside the handler
  and hides the original failure.
- Annotating `err: any`, or casting `err as Error`, turns off the check TypeScript 4.4 added:
  `useUnknownInCatchVariables`, part of `strict`, types the binding as `unknown` so it must be narrowed first.
- It presents as a handler that works for every error the author tried and breaks on the first odd value from
  a third-party library.

## Better

```typescript
try {
  await payments.charge(order);
} catch (err) {
  if (err instanceof PaymentError && err.code === "card_declined") {
    return { status: "declined", reason: err.message };
  }
  throw err;
}
```
