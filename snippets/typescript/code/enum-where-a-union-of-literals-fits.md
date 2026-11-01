---
aliases: []
language: typescript
typescript: ">=3.4"
severity: taste
category: maintainability
topic: typing
tags: [enums, literal-types, erasable-syntax, type-stripping]
keywords: ["enum ", "const enum", "export enum"]
signature: "An enum models a small closed set that a union of string literals or an as-const object would express, so the code carries non-erasable runtime syntax that plain type stripping cannot run."
distinguish: "Fine in a codebase that already standardises on enums and compiles with tsc, or where the named runtime object and numeric values are needed, such as mirroring a wire protocol's integer codes."
added: 2026-09-30
source: TypeScript handbook
---

# Enum where a union of literals fits

## Smell

```typescript
export enum Theme {
  Light,
  Dark,
  System,
}

export function applyTheme(theme: Theme): void {
  document.body.dataset.theme = Theme[theme].toLowerCase();
}

applyTheme(Theme.Dark);
```

## Why it's bad

- An `enum` is not a type annotation: it compiles to a real runtime object, with a reverse mapping from value
  to name for numeric members. It is one of the few TypeScript features that cannot be removed by deleting
  types.
- Node's built-in type stripping rejects enum declarations, and TypeScript 5.8's `--erasableSyntaxOnly` flag
  reports them as errors, so the file cannot run under `node file.ts` without a transform step.
- The numeric values `0`, `1`, `2` are what end up in logs, JSON, and storage, and reordering the members changes
  them.
- This is house taste rather than a rule: the handbook says an `as const` object may suffice, and the Google
  style guide permits plain enums while banning `const enum`.

## Better

```typescript
export const Theme = {
  Light: "light",
  Dark: "dark",
  System: "system",
} as const;
export type Theme = (typeof Theme)[keyof typeof Theme];

export function applyTheme(theme: Theme): void {
  document.body.dataset.theme = theme;
}

applyTheme("dark");
```
