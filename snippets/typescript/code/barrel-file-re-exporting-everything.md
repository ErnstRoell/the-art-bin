---
aliases: [barrel-file]
language: typescript
typescript: ">=3.0"
severity: trap
category: performance
topic: imports
tags: [barrel-files, modules, bundling, build-time, circular-imports, javascript]
keywords: ["export * from", "index.ts", "export { default as", "from \"../components\"", "from \"./utils\""]
signature: "An index file re-exports every module in a directory and the application imports through it, so importing one name loads, parses and transforms the whole directory and invites circular imports."
distinguish: "Fine as the single public entry point of a published package, the one file its package.json points at, as long as modules inside the package import each other directly."
added: 2026-09-30
source: TkDodo's blog
---

# Barrel file re-exporting everything

## Smell

```typescript
// src/components/index.ts
export * from "./Button";
export * from "./DataGrid";
export * from "./DatePicker";
export * from "./Chart";
export * from "./RichTextEditor";

// src/pages/Settings.tsx
import { Button } from "../components";
```

## Why it's bad

- Importing `Button` through the barrel makes the dev server, test runner and type checker load every module
  it re-exports, and everything those import. TkDodo reports a Next.js page dropping from over 11,000 modules
  to about 3,500 after internal barrels were removed.
- It works at first and degrades as the directory grows. Atlassian reported local unit tests about 50% faster
  and TypeScript highlighting over 30% faster after removing theirs.
- A module inside the directory that imports a sibling from `"."` or `"./index"` imports itself in a cycle,
  which JavaScript tolerates and bundlers sometimes do not.

## Better

```typescript
// src/pages/Settings.tsx
import { Button } from "../components/Button";
```
