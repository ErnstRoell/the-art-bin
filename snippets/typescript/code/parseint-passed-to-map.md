---
aliases: [map-parseint]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: stdlib-misuse
tags: [callbacks, parsing, arity, javascript]
keywords: [".map(parseInt)", "map(parseInt)", ".map(Number.parseInt)", ".forEach(parseInt)"]
signature: "parseInt is passed by reference to map, so the element index arrives as its radix argument and every element after the first is parsed in the wrong base."
distinguish: "Fine with a wrapper that forwards only the element, such as `(s) => Number.parseInt(s, 10)`, or with a function that ignores extra arguments, such as `map(Number)`."
added: 2026-09-30
source: MDN
---

# parseInt passed to map

## Smell

```typescript
function parsePorts(csv: string): number[] {
  return csv.split(",").map(parseInt);
}

parsePorts("8080,8081,8082"); // [8080, NaN, NaN]
```

## Why it's bad

- `map` calls its callback with the element, the index and the array. `parseInt` takes a string and a radix,
  so the second element is parsed with radix `1` and the third with radix `2`.
- TypeScript accepts it: the index is a `number`, which fits the optional `radix?: number` parameter, so the
  signature check that would catch most arity mistakes has nothing to say.
- The first element gets radix `0` and parses normally (`parseInt("1", 0)` is `1`), so a single-value test
  passes and the bug only shows with two or more values.

## Better

```typescript
function parsePorts(csv: string): number[] {
  return csv.split(",").map((part) => Number.parseInt(part, 10));
}
```
