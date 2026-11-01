---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [type-assertions, validation, trust-boundary, runtime-types]
keywords: ["JSON.parse(", "as User", "await res.json()", "response.json()", ".json() as", "localStorage.getItem("]
signature: "The result of JSON.parse or response.json is asserted or annotated to a domain type with no runtime check, so the type describes what the author hoped arrived rather than what did."
distinguish: "Fine when the parsed value is typed unknown and passed through a schema or a thorough guard before use, or when the JSON was produced by the same build moments earlier."
added: 2026-09-30
source: Effective TypeScript
---

# JSON.parse result cast to a type

## Smell

```typescript
interface User { id: number; email: string; roles: string[] }

async function fetchUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return (await res.json()) as User;
}

const prefs = JSON.parse(localStorage.getItem("prefs") ?? "{}") as Prefs;
const user = await fetchUser(7);
if (user.roles.includes("admin")) showAdminPanel();
```

## Why it's bad

- Type assertions are erased at compile time and insert no runtime check, so nothing verifies that the server
  actually sent `roles`; if it did not, `user.roles.includes` throws far from the fetch that caused it.
- `JSON.parse` and `Response.json()` can yield any JSON value — an object, an array, a string, a number, or
  `null` — and both are typed `any` in the standard library, so even the `as` is optional and the
  unchecked value flows straight into a typed return.
- It presents as a crash or a wrong branch after an API version bump or a stale `localStorage` entry, with a
  stack trace pointing at the consumer rather than the boundary.

## Better

```typescript
import { z } from "zod";

const User = z.object({ id: z.number(), email: z.string(), roles: z.array(z.string()) });
type User = z.infer<typeof User>;

async function fetchUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return User.parse(await res.json());
}
```
