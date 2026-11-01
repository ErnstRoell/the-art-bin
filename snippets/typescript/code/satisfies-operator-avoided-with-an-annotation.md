---
aliases: []
language: typescript
typescript: ">=4.9"
severity: taste
category: maintainability
topic: typing
tags: [satisfies, widening, type-annotations, config]
keywords: [": Record<", "const config:", "const routes:", "satisfies"]
signature: "A constant object is given a wide type annotation to check its shape, so the inferred literal keys and value types are discarded and later code has to narrow or assert what the compiler already knew."
distinguish: "Fine when the wider type is what callers should see, such as a mutable object that will later hold other members of the annotated type."
added: 2026-09-30
source: TypeScript 4.9 release notes
---

# satisfies operator avoided with an annotation

## Smell

```typescript
type Route = { path: string; auth: boolean };

const routes: Record<string, Route> = {
  home: { path: "/", auth: false },
  settings: { path: "/settings", auth: true },
};

routes.setings.path;
const name: keyof typeof routes = "anything";
```

## Why it's bad

- The annotation widens the object to `Record<string, Route>`, so `routes.setings` (a typo) is accepted and
  fails at runtime, where the inferred type would have rejected it.
- `keyof typeof routes` is now `string`, so helpers that take a route name accept any string.
- The TypeScript 4.9 release notes show the same trade-off with a colour palette: the annotation catches a
  misspelt key but widens `palette.green` to `string | RGB`, so calling `toUpperCase` on it is an error.

## Better

```typescript
type Route = { path: string; auth: boolean };

const routes = {
  home: { path: "/", auth: false },
  settings: { path: "/settings", auth: true },
} satisfies Record<string, Route>;

routes.settings.path;
const name: keyof typeof routes = "home";
```
