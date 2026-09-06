---
aliases: [missing-abstract-factory, mixed-product-family]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [abstract-factory, dispatch, configuration, coupling]
keywords: ["if cloud ==", "elif provider ==", "if backend ==", "= S3", "= Gcs", "os.environ["]
signature: "Each member of a product family is chosen by its own branch on the same setting, so nothing enforces that the parts assembled together come from one family."
distinguish: "Fine when the parts are genuinely independent choices that any deployment may combine freely, such as a storage backend and an unrelated cache."
added: 2026-09-06
source: refactoring.guru
---

# Product family selected part by part

## Smell

```python
def make_pipeline(cloud):
    if cloud == "aws":
        store = S3Store(BUCKET)
    else:
        store = GcsStore(BUCKET)

    if cloud == "aws":
        queue = SqsQueue(QUEUE_URL)
    else:
        queue = PubSubQueue(TOPIC)

    lock = DynamoLock(TABLE)        # correct on aws, quietly wrong on gcp
    return Pipeline(store, queue, lock)


def make_reporter(cloud):
    store = S3Store(BUCKET) if cloud == "aws" else GcsStore(BUCKET)
    return Reporter(store, DynamoLock(TABLE))   # the same omission, made again
```

## Why it's bad

- The family — store, queue, lock — is a set that must agree, but it is chosen one member at a time. Each
  branch is individually correct, so review of any single branch finds nothing wrong.
- The missing branch is the failure. `DynamoLock` on a GCP deployment does not fail at assembly; it fails when
  something first tries to take the lock, in an environment nobody runs locally, as a credentials error that
  reads like a misconfiguration rather than a wiring bug.
- Adding a third provider means finding every branch on `cloud` in the codebase, and the branches are only
  findable by knowing they exist. Adding a fourth family member means editing every assembly function.
- The set of valid combinations is never written down, so no test can assert it and no reader can check it.
- This is `equality-chain-instead-of-lookup-table` at one level up: not one chain that should be a table, but
  several chains on the same key that should be one object.

## Better

```python
class AwsParts:
    def store(self):
        return S3Store(BUCKET)

    def queue(self):
        return SqsQueue(QUEUE_URL)

    def lock(self):
        return DynamoLock(TABLE)


class GcpParts:
    def store(self):
        return GcsStore(BUCKET)

    def queue(self):
        return PubSubQueue(TOPIC)

    def lock(self):
        return SpannerLock(TABLE)


PARTS = {"aws": AwsParts, "gcp": GcpParts}


def make_pipeline(parts):
    return Pipeline(parts.store(), parts.queue(), parts.lock())


def make_reporter(parts):
    return Reporter(parts.store(), parts.lock())
```

Each family is one class, so a missing member is an `AttributeError` at start-up rather than a credentials
error in production, and `tuple(PARTS)` is the list of providers the program actually supports.
