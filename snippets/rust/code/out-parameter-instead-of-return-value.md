---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: functions
tags: [out-parameters, api-design, return-values]
keywords: ["out: &mut Vec<", "result: &mut", "-> bool {", "&mut Vec<", "errors: &mut Vec<"]
signature: "A function writes its result into a mutable reference argument and returns a flag or nothing, so the value it produces does not appear in its signature."
distinguish: "Fine when the caller reuses one buffer across many calls to avoid allocation, as with read_line or io::Read::read, and the parameter is documented as a buffer."
added: 2026-09-23
source: jeremy-wayland
---

# Out parameter instead of return value

## Smell

```rust
pub fn parse_rows(text: &str, rows: &mut Vec<Row>, errors: &mut Vec<String>) -> bool {
    for (number, line) in text.lines().enumerate() {
        match line.parse::<Row>() {
            Ok(row) => rows.push(row),
            Err(e) => errors.push(format!("line {}: {e}", number + 1)),
        }
    }
    errors.is_empty()
}
```

## Why it's bad

- The signature says it returns a `bool`. What it actually produces — rows and errors — is only discoverable
  by reading the body.
- Callers must construct empty vectors first and remember whether to clear them between calls. Passing a
  non-empty `rows` appends, which may or may not be what anyone intended.
- The `bool` duplicates information already in `errors`, and the two can disagree if a caller passes a
  non-empty `errors`.

## Better

```rust
pub fn parse_rows(text: &str) -> Result<Vec<Row>, Vec<String>> {
    let mut rows = Vec::new();
    let mut errors = Vec::new();
    for (number, line) in text.lines().enumerate() {
        match line.parse::<Row>() {
            Ok(row) => rows.push(row),
            Err(e) => errors.push(format!("line {}: {e}", number + 1)),
        }
    }
    if errors.is_empty() { Ok(rows) } else { Err(errors) }
}
```
