---
aliases: []
language: typescript
typescript: ">=3.9"
severity: trap
category: maintainability
topic: typing
tags: [suppression, compiler-directives, lint]
keywords: ["// @ts-ignore", "@ts-ignore", "@ts-nocheck"]
signature: "A type error is suppressed with ts-ignore, which stays silent even after the error is fixed, so the directive outlives its reason and later hides a new unrelated error on that line."
distinguish: "Fine as ts-expect-error with a description saying why, or as ts-ignore where the handbook suggests it, such as a line that errors under one TypeScript version and not another during an upgrade."
added: 2026-09-30
source: typescript-eslint
---

# ts-ignore instead of ts-expect-error

## Smell

```typescript
import legacyFormat from "legacy-format";

export function formatInvoice(invoice: Invoice): string {
  // @ts-ignore
  return legacyFormat(invoice, { locale: invoice.locale });
}
```

## Why it's bad

- `@ts-ignore` does nothing if the next line has no error, so when `legacy-format` ships correct types the
  comment stays, and nobody is told it is now dead.
- It then suppresses whatever error appears on that line next, such as `invoice.locale` being renamed, and that
  real bug compiles.
- With no description, a reviewer cannot tell which error was being suppressed or whether it is still expected.

## Better

```typescript
import legacyFormat from "legacy-format";

export function formatInvoice(invoice: Invoice): string {
  // @ts-expect-error -- legacy-format@2 types omit the options argument; fixed in v3
  return legacyFormat(invoice, { locale: invoice.locale });
}
```
