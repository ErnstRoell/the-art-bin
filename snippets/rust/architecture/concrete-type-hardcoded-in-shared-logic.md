---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [factory-method, generics, dependency-injection]
keywords: ["::new()", "fn run_sync(", "fn run_sync_s3(", "LocalStore::new(", "S3Store::new(", "let store ="]
signature: "A function that implements shared logic constructs the concrete type it works with, so a variant that needs a different type copies the whole function to change the one line that names it."
distinguish: "Fine when there is only one concrete type and no second one is planned, since a parameter for a choice nobody makes is only indirection."
added: 2026-09-23
source: refactoring.guru
---

# Concrete type hardcoded in shared logic

## Smell

```rust
pub fn sync(manifest: &Manifest) -> Result<SyncReport, SyncError> {
    let store = LocalStore::new("/var/backups");
    let mut report = SyncReport::default();
    for entry in &manifest.entries {
        if store.exists(&entry.key)? && store.checksum(&entry.key)? == entry.checksum {
            report.skipped += 1;
            continue;
        }
        store.put(&entry.key, &std::fs::read(&entry.path)?)?;
        report.uploaded += 1;
    }
    Ok(report)
}

pub fn sync_to_s3(manifest: &Manifest, bucket: &str) -> Result<SyncReport, SyncError> {
    let store = S3Store::new(bucket);
    let mut report = SyncReport::default();
    for entry in &manifest.entries {
        if store.exists(&entry.key)? && store.checksum(&entry.key)? == entry.checksum {
            report.skipped += 1;
            continue;
        }
        store.put(&entry.key, &std::fs::read(&entry.path)?)?;
        report.uploaded += 1;
    }
    Ok(report)
}
```

## Why it's bad

- The sync algorithm is identical, and the only difference is the line that constructs the store. Naming the
  concrete type inside the function forced a copy of everything around it.
- Testing `sync` needs a real `/var/backups`, because there is no way to hand it anything else.
- A third backend is a third copy, and a fix to the skip logic has to land in all of them.

## Better

```rust
pub trait Store {
    fn exists(&self, key: &str) -> Result<bool, SyncError>;
    fn checksum(&self, key: &str) -> Result<Checksum, SyncError>;
    fn put(&self, key: &str, bytes: &[u8]) -> Result<(), SyncError>;
}

pub fn sync(manifest: &Manifest, store: &impl Store) -> Result<SyncReport, SyncError> {
    let mut report = SyncReport::default();
    for entry in &manifest.entries {
        if store.exists(&entry.key)? && store.checksum(&entry.key)? == entry.checksum {
            report.skipped += 1;
            continue;
        }
        store.put(&entry.key, &std::fs::read(&entry.path)?)?;
        report.uploaded += 1;
    }
    Ok(report)
}

// sync(&manifest, &LocalStore::new("/var/backups"))
// sync(&manifest, &S3Store::new(bucket))
// sync(&manifest, &InMemoryStore::default())   in tests
```

The caller decides which store exists; the algorithm only needs something it can ask the three questions of.
