---
aliases: [lost-error-cause, rethrow-drops-original]
language: typescript
typescript: ">=4.6"
severity: trap
category: maintainability
topic: exceptions
tags: [error-handling, error-cause, es2022, javascript]
keywords: ["catch (err)", "throw new Error(", "{ cause", "preserve-caught-error"]
signature: "A catch block throws a new Error with more context but does not pass the caught error as its cause, so the original message and stack are discarded."
distinguish: "Fine when the new error is constructed with the cause option, or when the original is deliberately withheld at a trust boundary and logged before it is replaced."
added: 2026-09-30
source: MDN
---

# Error rethrown without its cause

## Smell

```typescript
async function loadInvoice(id: string): Promise<Invoice> {
  try {
    return await db.invoices.findOrThrow(id);
  } catch (err) {
    throw new Error(`could not load invoice ${id}`);
  }
}
```

## Why it's bad

- Adding context is right, but the new error replaces the old one. Whether the database timed out, refused the
  credentials or found no row is now gone, along with the stack that pointed at the failing query.
- The report that reaches you says only "could not load invoice 42", and the only way to learn why is to
  reproduce it.
- ES2022 added the `cause` option for exactly this, and ESLint's `preserve-caught-error` rule flags rethrows
  that omit it. TypeScript types it from 4.6 with `lib` or `target` set to `es2022`.

## Better

```typescript
async function loadInvoice(id: string): Promise<Invoice> {
  try {
    return await db.invoices.findOrThrow(id);
  } catch (err) {
    throw new Error(`could not load invoice ${id}`, { cause: err });
  }
}
```
