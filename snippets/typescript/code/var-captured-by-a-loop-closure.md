---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: control-flow
tags: [closures, scope, var, loops, javascript]
keywords: ["for (var ", "var i = 0", "var item =", "addEventListener(", "setTimeout(", ".onclick ="]
signature: "A callback created inside a loop captures a var-declared variable, so every callback shares the one function-scoped binding and sees its final value."
distinguish: "Fine when the loop variables are declared with let or const, which get a fresh binding per iteration, or when the callback runs synchronously before the next iteration."
added: 2026-09-30
source: MDN
---

# var captured by a loop closure

## Smell

```typescript
function attachHelp(fields: { id: string; help: string }[]): void {
  for (var i = 0; i < fields.length; i++) {
    var field = fields[i];
    document.getElementById(field.id)!.addEventListener("focus", () => {
      showHelp(field.help);
    });
  }
}
```

## Why it's bad

- `var` is function-scoped, so `field` is one variable shared by every listener. By the time any of them fires
  the loop has finished, and every field shows the last field's help text.
- The code reads correctly and type-checks, and the listener is attached to the right element each time, so
  the bug only shows when someone focuses a field other than the last.
- `let` and `const` are block-scoped and create a new binding for each iteration, which is why ESLint's
  `no-var` is the usual guard.

## Better

```typescript
function attachHelp(fields: { id: string; help: string }[]): void {
  for (const field of fields) {
    document.getElementById(field.id)!.addEventListener("focus", () => {
      showHelp(field.help);
    });
  }
}
```
