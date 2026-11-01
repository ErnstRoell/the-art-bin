---
aliases: [replace-without-global-flag]
language: typescript
typescript: ">=4.3"
severity: bug
category: correctness
topic: strings
tags: [strings, replace, regex, javascript]
keywords: [".replace(\" \"", ".replace(\"", ".replace('", ".replace(secret", ".replace(\",\""]
signature: "String replace is called with a string pattern as though it replaced every occurrence, when a string pattern replaces only the first."
distinguish: "Fine when only the first occurrence is meant to change, such as removing one leading prefix, or when the pattern is a regular expression with the g flag."
added: 2026-09-30
source: MDN
---

# String replace changes only the first match

## Smell

```typescript
function toSlug(title: string): string {
  return title.toLowerCase().replace(" ", "-");
}

function redact(log: string, secret: string): string {
  return log.replace(secret, "***");
}

toSlug("Code Smells In TypeScript"); // "code-smells in typescript"
```

## Why it's bad

- With a string pattern, `replace` changes the first occurrence and stops. The second and later spaces stay,
  and a secret that appears twice in a log line is redacted once and leaked once.
- Tests with one space or one occurrence pass, so the bug arrives with real data.
- The old fix, a regex with the `g` flag, needs the pattern escaped when it comes from a variable; `replaceAll`
  with a string does not, and it throws a `TypeError` if handed a regex without `g` instead of quietly
  replacing one match.

## Better

```typescript
function toSlug(title: string): string {
  return title.toLowerCase().replaceAll(" ", "-");
}

function redact(log: string, secret: string): string {
  return log.replaceAll(secret, "***"); // lib es2021
}
```
