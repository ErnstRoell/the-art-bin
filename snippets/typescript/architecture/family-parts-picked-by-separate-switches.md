---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [abstract-factory, switch, consistency, backends]
keywords: ["switch (config.cloud)", "case \"aws\":", "case \"gcp\":", "new S3Store(", "new GcsStore(", "process.env.CLOUD"]
signature: "Each member of a family of related parts is chosen by its own switch or ternary on the same setting, so nothing enforces that the parts assembled together come from one family."
distinguish: "Fine when the parts are genuinely independent choices that any deployment may combine freely, such as a logger and an unrelated cache."
added: 2026-09-30
source: refactoring.guru
---

# Family parts picked by separate switches

## Smell

```typescript
type Cloud = "aws" | "gcp";

export function makePipeline(config: { cloud: Cloud }): Pipeline {
  let store: BlobStore;
  switch (config.cloud) {
    case "aws": store = new S3Store(BUCKET); break;
    case "gcp": store = new GcsStore(BUCKET); break;
  }
  let queue: JobQueue;
  switch (config.cloud) {
    case "aws": queue = new SqsQueue(QUEUE_URL); break;
    case "gcp": queue = new PubSubQueue(TOPIC); break;
  }
  const lock = new DynamoLock(TABLE);   // right on aws, quietly wrong on gcp
  return new Pipeline(store, queue, lock);
}

export function makeReporter(): Reporter {
  const store = process.env.CLOUD === "gcp" ? new GcsStore(BUCKET) : new S3Store(BUCKET);
  return new Reporter(store, new DynamoLock(TABLE));   // the same omission, made again
}
```

## Why it's bad

- The store, queue and lock are a set that must agree, but each is chosen on its own. Every branch is
  individually correct, so reviewing any one of them finds nothing.
- The missing branch is the failure: `DynamoLock` on a GCP deployment compiles and assembles, then fails the
  first time something takes the lock, as a credentials error that reads like misconfiguration.
- `makeReporter` reads the setting from a different place, `process.env.CLOUD`, and defaults to AWS for any
  typo, so two parts of one program can disagree about which cloud they are on.
- A third cloud is a new `case` in every switch in every assembly function, and the ternaries do not get the
  exhaustiveness check a `switch` over a union can.

## Better

```typescript
interface CloudKit {
  store(): BlobStore;
  queue(): JobQueue;
  lock(): Lock;
}

const aws: CloudKit = {
  store: () => new S3Store(BUCKET),
  queue: () => new SqsQueue(QUEUE_URL),
  lock: () => new DynamoLock(TABLE),
};

const gcp: CloudKit = {
  store: () => new GcsStore(BUCKET),
  queue: () => new PubSubQueue(TOPIC),
  lock: () => new FirestoreLock(COLLECTION),
};

export const kits: Record<Cloud, CloudKit> = { aws, gcp };

export const makePipeline = (kit: CloudKit) => new Pipeline(kit.store(), kit.queue(), kit.lock());
export const makeReporter = (kit: CloudKit) => new Reporter(kit.store(), kit.lock());

// const kit = kits[config.cloud];   read once, at startup
```

The setting is read once to pick a kit, and every part comes from it. `Record<Cloud, CloudKit>` makes a new
cloud a compile error until its whole kit exists, and a kit missing a member does not type-check.
