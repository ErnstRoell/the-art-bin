---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: functions
tags: [template-method, traits, default-methods, duplication]
keywords: ["fn import_csv(", "fn import_json(", "log::info!(\"importing", "for record in", "tx.commit()", "Ok(count)"]
signature: "Two variants of one procedure are written as two copies of the whole procedure, so the steps they share are duplicated and drift apart."
distinguish: "Fine when the variants share only incidental lines and are expected to diverge, so a shared skeleton would be a constraint rather than a help."
added: 2026-09-23
source: refactoring.guru
---

# Procedure duplicated per variant

## Smell

```rust
pub fn import_csv(path: &Path, db: &Db) -> Result<usize, ImportError> {
    log::info!("importing {}", path.display());
    let text = std::fs::read_to_string(path)?;
    let records = parse_csv(&text)?;
    let mut tx = db.begin()?;
    let mut count = 0;
    for record in records {
        validate(&record)?;
        tx.insert(&record)?;
        count += 1;
    }
    tx.commit()?;
    log::info!("imported {count} records");
    Ok(count)
}

pub fn import_json(path: &Path, db: &Db) -> Result<usize, ImportError> {
    log::info!("importing {}", path.display());
    let text = std::fs::read_to_string(path)?;
    let records: Vec<Record> = serde_json::from_str(&text)?;
    let tx = db.begin()?;
    let mut count = 0;
    for record in records {
        tx.insert(&record)?;   // validation was never copied across
        count += 1;
    }
    tx.commit()?;
    Ok(count)
}
```

## Why it's bad

- The functions differ in one line, parsing, and share eleven. Each shared line is now maintained twice, and
  the copies have already drifted: JSON skips validation and the closing log.
- A fix to the shared steps, such as batching inserts, has to be found and applied in every copy. The copy
  nobody remembered keeps the old behaviour.
- A third format means a third copy, which is how a module ends up with five importers that each handle
  errors slightly differently.

## Better

```rust
pub trait Format {
    fn parse(&self, text: &str) -> Result<Vec<Record>, ImportError>;
}

pub struct Csv;
pub struct Json;

impl Format for Csv {
    fn parse(&self, text: &str) -> Result<Vec<Record>, ImportError> {
        parse_csv(text)
    }
}

impl Format for Json {
    fn parse(&self, text: &str) -> Result<Vec<Record>, ImportError> {
        Ok(serde_json::from_str(text)?)
    }
}

pub fn import(path: &Path, db: &Db, format: &impl Format) -> Result<usize, ImportError> {
    log::info!("importing {}", path.display());
    let records = format.parse(&std::fs::read_to_string(path)?)?;
    let tx = db.begin()?;
    for record in &records {
        validate(record)?;
        tx.insert(record)?;
    }
    tx.commit()?;
    log::info!("imported {} records", records.len());
    Ok(records.len())
}
```

The skeleton is written once and the variants supply only the step that differs. When a step has a sensible
default, it can be a default method on the trait.
