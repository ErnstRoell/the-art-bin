---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [type-assertions, unsoundness, casts]
keywords: ["as unknown as", "as any as", "unknown as"]
signature: "A value is cast through unknown or any to a type the compiler refused as a direct assertion, so the one warning that the types do not overlap is deliberately bypassed."
distinguish: "Fine inside a small well-typed helper whose signature is correct, with a comment explaining why the conversion holds, or in a test fixture that builds a deliberately partial mock."
added: 2026-09-30
source: TypeScript handbook
---

# Double assertion through unknown

## Smell

```typescript
interface ApiUser { user_id: string; display_name: string }
interface User { id: number; name: string }

function toUser(raw: ApiUser): User {
  return raw as unknown as User;
}

const user = toUser(await fetchApiUser());
console.log(user.name.length);
```

## Why it's bad

- A direct `raw as User` is rejected because the types do not sufficiently overlap. That error was correct:
  the fields have different names and `id` is a different type. Routing through `unknown` silences it.
- Assertions are removed at compile time with no runtime check, so `user.name` is `undefined` at runtime and
  `.length` throws, even though every line type-checks.
- Once in place, the double cast survives later changes to either interface; the compiler will never again
  compare them at this site.

## Better

```typescript
function toUser(raw: ApiUser): User {
  return { id: Number(raw.user_id), name: raw.display_name };
}

const user = toUser(await fetchApiUser());
console.log(user.name.length);
```
