---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: typing
tags: [literal-types, unions, magic-strings, stringly-typed]
keywords: ["status: string", "kind: string", "mode: string", "type: string", "=== \""]
signature: "A parameter or field typed string only ever holds one of a few known values, so a typo or an unsupported value compiles and the valid set lives only in comparisons scattered through the code."
distinguish: "Fine when the value really is open-ended, such as a user's display name or a free-form tag, or at a parsing boundary that immediately narrows the string to a literal union."
added: 2026-09-30
source: Effective TypeScript
---

# String parameter for a closed set

## Smell

```typescript
interface Ticket {
  id: string;
  status: string;
}

function isOpen(ticket: Ticket): boolean {
  return ticket.status === "open" || ticket.status === "in-progress";
}

setStatus(ticket, "in_progress");
```

## Why it's bad

- `"in_progress"` is not `"in-progress"`, and `string` accepts both, so the ticket silently drops out of every
  "open" filter.
- The valid values are discoverable only by reading comparisons like the one in `isOpen`; editors cannot
  complete them and the compiler cannot flag a comparison against a value that never occurs.
- A switch over `status` cannot be checked for exhaustiveness, because `string` has no finite set of members.

## Better

```typescript
type TicketStatus = "open" | "in-progress" | "closed";

interface Ticket {
  id: string;
  status: TicketStatus;
}

function isOpen(ticket: Ticket): boolean {
  return ticket.status === "open" || ticket.status === "in-progress";
}

setStatus(ticket, "in-progress");
```
