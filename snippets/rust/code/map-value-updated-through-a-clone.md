---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: correctness
topic: stdlib-misuse
tags: [hashmap, entry-api, lost-update]
keywords: [".get(&", ".cloned().unwrap_or_default()", ".unwrap_or_default()", "contains_key(", ".entry(", "or_default()"]
signature: "A map value is fetched as a clone or default, modified, and never written back, so the update is dropped instead of stored."
distinguish: "Fine when the modified copy is deliberately a new value that is inserted back or used locally, and the map is meant to stay unchanged."
added: 2026-09-23
source: jeremy-wayland
---

# Map value updated through a clone

## Smell

```rust
pub fn tag_file(tags: &mut HashMap<String, Vec<String>>, file: &str, tag: &str) {
    let mut file_tags = tags.get(file).cloned().unwrap_or_default();
    file_tags.push(tag.to_owned());
}
```

## Why it's bad

- `get(...).cloned()` produces a copy owned by this function. The push lands in the copy, which is dropped at
  the end of the scope, and the map never changes.
- It compiles without warning, because `file_tags` is used. The shape usually appears after fighting the
  borrow checker over `get_mut`, where `.cloned()` made the error go away.
- It presents as tags that are "saved" and then never shown, with no error anywhere.

## Better

```rust
pub fn tag_file(tags: &mut HashMap<String, Vec<String>>, file: &str, tag: &str) {
    tags.entry(file.to_owned()).or_default().push(tag.to_owned());
}
```
