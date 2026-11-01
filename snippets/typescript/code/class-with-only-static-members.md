---
aliases: [static-utility-class]
language: typescript
typescript: ">=3.0"
severity: taste
category: readability
topic: classes
tags: [classes, static, namespacing, modules, javascript]
keywords: ["static ", "class Utils", "class Helpers", "class StringUtils", "private constructor() {}", "Utils."]
signature: "A class holds only static methods and constants and is never instantiated, so it is a namespace wrapped around what the module already provides."
distinguish: "Fine when the class also has instances, such as static factories alongside instance methods, or when a framework requires a class so it can carry decorators."
added: 2026-09-30
source: typescript-eslint no-extraneous-class
---

# Class with only static members

## Smell

```typescript
export class StringUtils {
  static readonly ELLIPSIS = "…";

  static truncate(text: string, max: number): string {
    return text.length <= max ? text : text.slice(0, max - 1) + StringUtils.ELLIPSIS;
  }

  static slugify(text: string): string {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  }
}
```

## Why it's bad

- The module is already the namespace; the class adds a second one, a type that can be `new`ed to no purpose,
  and a `StringUtils.` prefix at every call site.
- typescript-eslint's `no-extraneous-class` notes that static members are harder to autocomplete, harder to
  check for unused members than individual exports.
- The Google TypeScript Style Guide says not to create container classes with static methods or properties
  for the sake of namespacing.

## Better

```typescript
export const ELLIPSIS = "…";

export function truncate(text: string, max: number): string {
  return text.length <= max ? text : text.slice(0, max - 1) + ELLIPSIS;
}

export function slugify(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-");
}

// callers that want the prefix: import * as strings from "./strings";
```
