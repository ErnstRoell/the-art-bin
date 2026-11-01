---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: stdlib-misuse
tags: [prototype, dictionaries, map, javascript, prototype-pollution]
keywords: ["= {}", "Record<string,", "[key: string]:", "[key] =", "in counts", "__proto__"]
signature: "A plain object literal is used as a dictionary keyed by external strings, so keys such as __proto__ or constructor collide with the prototype and lookups or writes go to Object.prototype."
distinguish: "Fine when the keys are a fixed, compile-time set such as a Record over a literal union, or when the object is created with a null prototype."
added: 2026-09-30
source: MDN
---

# Plain object used as a dictionary

## Smell

```typescript
const counts: Record<string, number> = {};

function countWords(text: string): Record<string, number> {
  for (const word of text.split(/\s+/)) {
    counts[word] = (counts[word] ?? 0) + 1;
  }
  return counts;
}

countWords("the constructor of the __proto__");
```

## Why it's bad

- An object has a prototype, so it contains default keys that collide with your own: `counts["constructor"]` is
  a function before anything is stored, so the count for "constructor" becomes the string
  `"function Object() { [native code] }1"`.
- `counts["__proto__"] = 1` goes to the prototype setter, which ignores the number, so that word is silently
  never counted; when an attacker controls nested keys, the same pattern writes to `Object.prototype` itself.
- `word in counts` and `for...in` both see inherited properties, so membership checks lie.

## Better

```typescript
function countWords(text: string): Map<string, number> {
  const counts = new Map<string, number>();
  for (const word of text.split(/\s+/)) {
    counts.set(word, (counts.get(word) ?? 0) + 1);
  }
  return counts;
}
```
