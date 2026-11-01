---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: mutability
tags: [arrays, delete, sparse-arrays, javascript]
keywords: ["delete arr[", "delete items[", "delete tags[", "delete list[", "delete this.items["]
signature: "An element is removed from an array with the delete operator, which leaves an empty slot and does not change the length."
distinguish: "Fine on a plain object used as a dictionary, where removing a key is the point and there is no length to keep consistent."
added: 2026-09-30
source: MDN
---

# delete on an array element

## Smell

```typescript
function removeTag(tags: string[], tag: string): void {
  const index = tags.indexOf(tag);
  if (index !== -1) {
    delete tags[index];
  }
}

const tags = ["a", "b", "c"];
removeTag(tags, "b");
tags.length;     // 3
tags.join(", "); // "a, , c"
```

## Why it's bad

- `delete` removes the property but not the position: the array becomes sparse with an empty slot, and
  `length` is unchanged, even when the deleted element was the last one.
- The type is still `string[]`, but `tags[1]` is now `undefined`, and TypeScript accepts `delete` on an array
  index without complaint.
- Iteration disagrees about the hole: `forEach` and `map` skip it, `for...of` visits it as `undefined` and
  `join` prints it as an empty string, so counts, rendered lists and serialised output drift apart.

## Better

```typescript
function removeTag(tags: string[], tag: string): void {
  const index = tags.indexOf(tag);
  if (index !== -1) {
    tags.splice(index, 1);
  }
}

const withoutB = tags.filter((t) => t !== "b"); // when a new array is fine
```
