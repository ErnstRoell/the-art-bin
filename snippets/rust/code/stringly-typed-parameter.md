---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: maintainability
topic: typing
tags: [enums, api-design, magic-strings]
keywords: ['format: &str', 'mode: &str', '== "json"', '"csv" =>', 'match mode {', "kind: String"]
signature: "A string parameter selects behaviour from a fixed set of magic values, so a typo is only caught at runtime if at all."
distinguish: "Fine at a parsing boundary such as a CLI flag or config file, provided the string is converted into an enum there and nowhere else."
added: 2026-09-23
source: jeremy-wayland
---

# Stringly-typed parameter

## Smell

```rust
pub fn export(rows: &[Row], format: &str) -> Vec<u8> {
    match format {
        "json" => to_json(rows),
        "csv" => to_csv(rows),
        _ => Vec::new(),
    }
}

let bytes = export(&rows, "JSON");
```

## Why it's bad

- `"JSON"` is not `"json"`, so this call returns an empty file rather than an error, and the empty file is
  what gets uploaded.
- The set of valid formats lives only in the match arms. Callers learn it by reading the body, and editors
  cannot complete it.
- Adding `"parquet"` changes no signature, so no caller is told, and the compiler cannot check exhaustiveness
  across the functions that branch on the same string.

## Better

```rust
pub enum Format { Json, Csv }

impl std::str::FromStr for Format {
    type Err = UnknownFormat;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_ascii_lowercase().as_str() {
            "json" => Ok(Format::Json),
            "csv" => Ok(Format::Csv),
            _ => Err(UnknownFormat(s.to_owned())),
        }
    }
}

pub fn export(rows: &[Row], format: Format) -> Vec<u8> {
    match format {
        Format::Json => to_json(rows),
        Format::Csv => to_csv(rows),
    }
}
```
