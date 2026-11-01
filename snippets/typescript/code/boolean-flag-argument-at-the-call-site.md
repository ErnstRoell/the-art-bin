---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: readability
topic: functions
tags: [api-design, call-sites, javascript, options-object]
keywords: [", true)", ", false)", "(true,", "(false,", ": boolean,", ": boolean)"]
signature: "A boolean positional parameter switches the function between modes, so the call site reads as a bare true or false that means nothing without the signature."
distinguish: "Fine when the boolean is the value being set rather than a mode, such as setVisible(true), where the function name already says what true means."
added: 2026-09-30
source: Martin Fowler, FlagArgument
---

# Boolean flag argument at the call site

## Smell

```typescript
function renderUser(user: User, compact: boolean, showEmail: boolean): string {
  // ...
}

const row = renderUser(user, true, false);
```

## Why it's bad

- `renderUser(user, true, false)` cannot be read without opening the signature, and swapping the two literals
  still compiles because both are `boolean`.
- A flag argument means the function does different things depending on its value, which Fowler argues is
  clearer as separately named operations.
- A third mode, such as a card layout, does not fit a `boolean` and forces another positional flag whose
  combinations with the first include nonsense.

## Better

```typescript
interface RenderOptions {
  layout: "compact" | "full";
  showEmail?: boolean;
}

function renderUser(user: User, { layout, showEmail = false }: RenderOptions): string {
  // ...
}

const row = renderUser(user, { layout: "compact" });
```
