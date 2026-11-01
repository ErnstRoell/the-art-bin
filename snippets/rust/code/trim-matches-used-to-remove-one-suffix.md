---
aliases: []
language: rust
rust: ">=1.45"
severity: bug
category: correctness
topic: strings
tags: [strings, suffixes, patterns]
keywords: [".trim_end_matches(\"", ".trim_start_matches(\"", ".trim_end_matches(&[", ".trim_matches(", "strip_suffix("]
signature: "A trim_matches call is written as though it removed one prefix or suffix, when it repeatedly strips every match or, given a char array, any of those characters."
distinguish: "Fine when stripping every repetition is the intent, such as trimming all trailing slashes or zeros."
added: 2026-09-23
source: jeremy-wayland
---

# Trim matches used to remove one suffix

## Smell

```rust
pub fn base_name(file: &str) -> &str {
    file.trim_end_matches(".txt")
}

pub fn strip_extension(file: &str) -> &str {
    file.trim_end_matches(&['.', 't', 'x'][..])
}
```

## Why it's bad

- `trim_end_matches` repeats until the pattern stops matching, so `base_name("notes.txt.txt")` is `"notes"`,
  not `"notes.txt"`.
- With a char array the pattern is a set of characters, so `strip_extension("context.txt")` strips `t`, `x`,
  `t`, `.`, `t`, `x` and returns `"conte"`.
- Neither reports whether the suffix was there, so a file without it passes through unchanged and the caller
  cannot tell the difference.

## Better

```rust
pub fn base_name(file: &str) -> &str {
    file.strip_suffix(".txt").unwrap_or(file)
}

pub fn file_stem(file: &Path) -> Option<&OsStr> {
    file.file_stem()
}
```
