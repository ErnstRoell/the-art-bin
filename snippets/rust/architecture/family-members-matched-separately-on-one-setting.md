---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: classes
tags: [abstract-factory, traits, consistency, backends]
keywords: ["match backend {", "Backend::Postgres =>", "Backend::Sqlite =>", "config.backend", "PgQueue::new(", "SqliteQueue::new("]
signature: "Each member of a family of related parts is chosen by its own match on the same setting, so nothing enforces that the parts assembled together come from one family."
distinguish: "Fine when the parts are genuinely independent and mixing them is valid, such as choosing a logger and a database separately."
added: 2026-09-23
source: refactoring.guru
---

# Family members matched separately on one setting

## Smell

```rust
pub fn build_services(config: &Config) -> Services {
    let store: Box<dyn Store> = match config.backend {
        Backend::Postgres => Box::new(PgStore::connect(&config.url)),
        Backend::Sqlite => Box::new(SqliteStore::open(&config.path)),
    };
    let queue: Box<dyn Queue> = match config.backend {
        Backend::Postgres => Box::new(PgQueue::connect(&config.url)),
        Backend::Sqlite => Box::new(SqliteQueue::open(&config.path)),
    };
    let migrator: Box<dyn Migrator> = match config.migration_backend {  // a second setting
        Backend::Postgres => Box::new(PgMigrator::new(&config.url)),
        Backend::Sqlite => Box::new(SqliteMigrator::new(&config.path)),
    };
    Services { store, queue, migrator }
}
```

## Why it's bad

- The store, queue and migrator must agree on one database; migrating Postgres and then reading SQLite is not
  a configuration anyone wants. Each `match` makes the choice independently, and one already reads a different
  setting.
- A new backend, such as MySQL, is an arm in every match, in every function that builds a part. Missing one
  compiles if that match happens to have a fallback arm.
- The family has no name in the code. "Postgres support" is scattered across however many matches pick a
  Postgres part.

## Better

```rust
pub trait BackendFamily {
    fn store(&self) -> Box<dyn Store>;
    fn queue(&self) -> Box<dyn Queue>;
    fn migrator(&self) -> Box<dyn Migrator>;
}

pub struct Postgres { url: String }
pub struct Sqlite { path: PathBuf }

impl BackendFamily for Postgres {
    fn store(&self) -> Box<dyn Store> { Box::new(PgStore::connect(&self.url)) }
    fn queue(&self) -> Box<dyn Queue> { Box::new(PgQueue::connect(&self.url)) }
    fn migrator(&self) -> Box<dyn Migrator> { Box::new(PgMigrator::new(&self.url)) }
}

pub fn build_services(family: &dyn BackendFamily) -> Services {
    Services { store: family.store(), queue: family.queue(), migrator: family.migrator() }
}
```

The setting is read once to pick a family, and every part comes from it. A new backend is one type, and the
compiler lists what it must provide.
