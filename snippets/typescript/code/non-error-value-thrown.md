---
aliases: [throw-string, throw-literal]
language: typescript
typescript: ">=3.0"
severity: trap
category: maintainability
topic: exceptions
tags: [error-handling, stack-trace, promise, javascript]
keywords: ['throw "', "throw '", "throw `", "throw {", "Promise.reject(\"", "reject(\"", "only-throw-error", "no-throw-literal"]
signature: "A string, number or plain object is thrown or used as a promise rejection reason instead of an Error, so no stack trace is captured and catch sites cannot rely on name or message."
distinguish: "Fine when throwing an instance of Error or a subclass, or when rethrowing a caught value unchanged."
added: 2026-09-30
source: typescript-eslint
---

# Non-Error value thrown

## Smell

```typescript
function parseAmount(input: string): number {
  const value = Number(input);
  if (Number.isNaN(value)) {
    throw `invalid amount: ${input}`;
  }
  if (value < 0) {
    throw { code: "NEGATIVE", value };
  }
  return value;
}
```

## Why it's bad

- An `Error` records where it was constructed; a string or object does not. The Google TypeScript Style Guide
  notes that a thrown non-Error does not populate stack trace information, so the log line says what went
  wrong but not where.
- Handlers written as `err instanceof Error` or `err.message` miss these values entirely, so they fall through
  to a generic branch or print `[object Object]`.
- The same applies to `Promise.reject("...")` and `reject(...)` in a promise executor; typescript-eslint's
  `only-throw-error` and `prefer-promise-reject-errors` flag both.

## Better

```typescript
class AmountError extends Error {
  constructor(readonly code: "INVALID" | "NEGATIVE", readonly input: string) {
    super(`${code.toLowerCase()} amount: ${input}`);
    this.name = "AmountError";
  }
}

function parseAmount(input: string): number {
  const value = Number(input);
  if (Number.isNaN(value)) throw new AmountError("INVALID", input);
  if (value < 0) throw new AmountError("NEGATIVE", input);
  return value;
}
```
