---
aliases: [default-export]
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: imports
tags: [modules, exports, refactoring, javascript]
keywords: ["export default", "export default function", "export default class", "export default {"]
signature: "A module exposes its main value as a default export, so every importer picks its own name for it and a rename or a wrong import is invisible to the compiler."
distinguish: "Fine where a framework or API requires a default export, such as the module loaded by React.lazy or a framework's page and config files."
added: 2026-09-30
source: Google TypeScript Style Guide
---

# Default export of a module

## Smell

```typescript
// user-service.ts
export default function (id: string): Promise<User> {
  return db.users.findOne(id);
}

// profile.ts
import getUser from "./user-service";
// settings.ts
import fetchUser from "./user-service";
// admin.ts
import loadAccount from "./user-service";
```

## Why it's bad

- A default export has no canonical name, so the same function is `getUser`, `fetchUser` and `loadAccount`
  depending on the file, and searching for its callers means searching for every alias.
- Importing a named export that does not exist is a compile error; a default import accepts any name, so when
  the module's default changes meaning the importers still compile.
- The Google TypeScript Style Guide requires named exports in all code for exactly these reasons.

## Better

```typescript
// user-service.ts
export function findUser(id: string): Promise<User> {
  return db.users.findOne(id);
}

// profile.ts, settings.ts, admin.ts
import { findUser } from "./user-service";
```
