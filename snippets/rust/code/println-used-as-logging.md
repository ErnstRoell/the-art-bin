---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: io
tags: [logging, stdout, observability]
keywords: ["println!(\"", "eprintln!(\"", "dbg!(", "println!(\"DEBUG", "println!(\"Processing"]
signature: "A library or long-running service reports progress and errors with println or eprintln, so the output has no level, timestamp, target or way to turn it off."
distinguish: "Fine in a command-line tool whose output is the program's product, such as the result written to stdout, or in examples and throwaway scripts."
added: 2026-09-23
source: jeremy-wayland
---

# Println used as logging

## Smell

```rust
pub fn import(path: &Path, db: &Db) -> Result<usize, ImportError> {
    println!("Importing {}", path.display());
    let rows = read_rows(path)?;
    for (index, row) in rows.iter().enumerate() {
        if let Err(e) = db.insert(row) {
            println!("ERROR row {index}: {e}");
        }
    }
    println!("Done");
    Ok(rows.len())
}
```

## Why it's bad

- Stdout belongs to the program that calls this. A CLI that pipes its JSON output to `jq` now receives
  "Importing ..." in the middle of its data.
- `println!` has no level, so an operator cannot silence progress while keeping errors, and "ERROR" is a word
  in a string rather than something a log pipeline can filter on.
- Nothing records the time, the module or the request that produced a line, so interleaved output from
  concurrent imports cannot be untangled.

## Better

```rust
pub fn import(path: &Path, db: &Db) -> Result<usize, ImportError> {
    log::info!("importing {}", path.display());
    let rows = read_rows(path)?;
    for (index, row) in rows.iter().enumerate() {
        if let Err(e) = db.insert(row) {
            log::error!("row {index} of {}: {e}", path.display());
        }
    }
    log::debug!("imported {} rows", rows.len());
    Ok(rows.len())
}
```
