---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [factory-method, dependency-injection, duplication, testability]
keywords: ["new LocalStore(", "new S3Store(", "async function sync", "syncToS3(", "const store = new", "implements Store"]
signature: "A function that implements shared logic constructs with new the concrete class it works with, so a variant needing a different class copies the whole function to change the one line that names it."
distinguish: "Fine when there is one concrete class and no test needs another, since a parameter or factory for a choice nobody makes is only indirection."
added: 2026-09-30
source: refactoring.guru
---

# Class newed inside shared logic

## Smell

```typescript
export async function sync(manifest: Manifest): Promise<SyncReport> {
  const store = new LocalStore("/var/backups");
  const report = { uploaded: 0, skipped: 0 };
  for (const entry of manifest.entries) {
    if ((await store.exists(entry.key)) && (await store.checksum(entry.key)) === entry.checksum) {
      report.skipped++;
      continue;
    }
    await store.put(entry.key, await readFile(entry.path));
    report.uploaded++;
  }
  return report;
}

export async function syncToS3(manifest: Manifest, bucket: string): Promise<SyncReport> {
  const store = new S3Store(bucket);
  const report = { uploaded: 0, skipped: 0 };
  for (const entry of manifest.entries) {
    if ((await store.exists(entry.key)) && (await store.checksum(entry.key)) === entry.checksum) {
      report.skipped++;
      continue;
    }
    await store.put(entry.key, await readFile(entry.path));
    report.uploaded++;
  }
  return report;
}
```

## Why it's bad

- The sync algorithm is identical in both, and the only difference is the `new` on the first line. Naming the
  concrete class inside the function forced a copy of everything around it.
- The copies drift: a fix to the skip check lands in whichever function the bug was reported against, and the
  other keeps the bug.
- Testing `sync` needs a real `/var/backups`, because there is no way to hand it anything else short of
  mocking the module that exports `LocalStore`.

## Better

```typescript
export interface Store {
  exists(key: string): Promise<boolean>;
  checksum(key: string): Promise<string>;
  put(key: string, bytes: Uint8Array): Promise<void>;
}

export async function sync(manifest: Manifest, store: Store): Promise<SyncReport> {
  const report = { uploaded: 0, skipped: 0 };
  for (const entry of manifest.entries) {
    if ((await store.exists(entry.key)) && (await store.checksum(entry.key)) === entry.checksum) {
      report.skipped++;
      continue;
    }
    await store.put(entry.key, await readFile(entry.path));
    report.uploaded++;
  }
  return report;
}

// sync(manifest, new LocalStore("/var/backups"))
// sync(manifest, new S3Store(bucket))
// sync(manifest, { exists: async () => false, checksum: async () => "", put: async () => {} })   in tests
```

The caller decides which store exists. TypeScript's structural typing means the test double is an object
literal, with no subclass and no factory method needed; pass a `() => Store` instead only when the algorithm
must create stores itself.
