---
aliases: [missing-template-method, pipeline-copied-per-format]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: functions
tags: [template-method, duplication, hooks, pipelines]
keywords: ["def import_", "def load_", "with transaction()", "log.info(", "for record in", "return len("]
signature: "Two variants of one procedure are written as two copies of the whole procedure, so the steps they share are duplicated and drift apart."
distinguish: "Fine when the two procedures only look alike, sharing a shape but no reason to change together."
added: 2026-09-06
source: refactoring.guru
---

# Algorithm skeleton duplicated per variant

## Smell

```python
def import_csv(path):
    with open(path, encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    records = [dict(zip(rows[0], row)) for row in rows[1:]]
    records = [r for r in records if r.get("id")]
    with transaction():
        for record in records:
            upsert(record)
    log.info("imported %d from %s", len(records), path)
    return len(records)


def import_json(path):
    records = json.loads(Path(path).read_text(encoding="utf-8"))["items"]
    records = [r for r in records if r.get("id")]
    with transaction():
        for record in records:
            upsert(record)
    log.info("imported %d from %s", len(records), path)
    return len(records)          # six shared lines, copied, and free to drift
```

## Why it's bad

- The two functions differ in one step — how bytes become records — and are duplicated in the other five:
  filtering, the transaction, the upsert loop, the log line, the return value.
- Fixes land on one copy. When the filter grows to skip blank ids as well as missing ones, it is fixed where
  the bug was reported, and the other importer keeps loading rows the database then rejects.
- A third format copies the skeleton again, so the cost of a format is the length of the pipeline rather than
  the size of the difference.
- The shared part cannot be tested once. "Import runs in one transaction" is a property of both functions and
  has to be asserted against each of them separately, forever.
- The duplication is invisible to a reviewer looking at one function at a time, which is why it survives: each
  function is short, clear and correct on its own.

## Better

```python
class Importer:
    """The skeleton, written once. Subclasses own the one step that varies."""

    def run(self, path):
        records = [r for r in self.parse(path) if r.get("id")]
        with transaction():
            for record in records:
                upsert(record)
        log.info("imported %d from %s", len(records), path)
        return len(records)

    def parse(self, path):
        raise NotImplementedError


class CsvImporter(Importer):
    def parse(self, path):
        with open(path, encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        return [dict(zip(rows[0], row)) for row in rows[1:]]


class JsonImporter(Importer):
    def parse(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))["items"]
```

A new format is a `parse` method, a fix to the pipeline lands in both importers at once, and the transaction
property is tested once against `Importer` with a fake `parse`.
