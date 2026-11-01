---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: control-flow
tags: [unions, exhaustiveness, never, switch]
keywords: ["switch (", "case \"", "default:", ".kind)", ".type)"]
signature: "A switch over a union handles today's members with no never check or exhaustive return type, so a member added later falls through silently instead of failing to compile."
distinguish: "Fine when the function has a non-void return type that makes a missing case a compile error, when the switch-exhaustiveness-check lint rule is on, or when the switch is over an open type such as string where a default is the correct behaviour."
added: 2026-09-30
source: TypeScript handbook
---

# Switch without an exhaustiveness check

## Smell

```typescript
type Event =
  | { kind: "signup"; email: string }
  | { kind: "purchase"; amount: number };

function track(event: Event): void {
  switch (event.kind) {
    case "signup":
      sendWelcome(event.email);
      break;
    case "purchase":
      recordRevenue(event.amount);
      break;
  }
}
```

## Why it's bad

- When someone adds `{ kind: "refund"; amount: number }` to `Event`, `track` still compiles and simply does
  nothing for refunds, so revenue is overstated with no error anywhere.
- Because the function returns `void`, the compiler has no missing return to complain about, and a plain
  `default: break` would hide the gap just as well.
- The union's definition and its consumers are usually in different files, so the author adding a member has no
  prompt to find every switch that needs updating.

## Better

```typescript
function track(event: Event): void {
  switch (event.kind) {
    case "signup":
      sendWelcome(event.email);
      break;
    case "purchase":
      recordRevenue(event.amount);
      break;
    default: {
      const unhandled: never = event;
      throw new Error(`unhandled event: ${JSON.stringify(unhandled)}`);
    }
  }
}
```
