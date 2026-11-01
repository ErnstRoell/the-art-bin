---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: functions
tags: [template-method, duplication, hooks, pipelines]
keywords: ["async function importCsv(", "async function importJson(", "db.transaction(", "tx.upsert(", "log.info(`imported", "return valid.length"]
signature: "Two variants of one procedure are written as two copies of the whole procedure, so the steps they share are duplicated and drift apart."
distinguish: "Fine when the two procedures only look alike, sharing a shape but no reason to change together."
added: 2026-09-30
source: refactoring.guru
---

# Import function copied per file format

## Smell

```typescript
export async function importCsv(path: string): Promise<number> {
  const [header, ...rows] = (await readFile(path, "utf8")).trim().split("\n").map((l) => l.split(","));
  const records: Row[] = rows.map((row) => Object.fromEntries(header.map((h, i) => [h, row[i]])));
  const valid = records.filter((r) => r.id);
  await db.transaction(async (tx) => {
    for (const record of valid) await tx.upsert("items", record);
  });
  log.info(`imported ${valid.length} from ${path}`);
  return valid.length;
}

export async function importJson(path: string): Promise<number> {
  const records: Row[] = JSON.parse(await readFile(path, "utf8")).items;
  const valid = records.filter((r) => r.id);
  await db.transaction(async (tx) => {
    for (const record of valid) await tx.upsert("items", record);
  });
  log.info(`imported ${valid.length} from ${path}`);
  return valid.length;                    // six shared lines, copied and free to drift
}
```

## Why it's bad

- The two functions differ in one step, how text becomes records, and duplicate the rest: the filter, the
  transaction, the upsert loop, the log line and the return value.
- Fixes land on one copy. When the filter grows to skip blank ids as well as missing ones, it is fixed where
  the bug was reported, and the other importer keeps loading rows the database then rejects.
- A third format copies the skeleton again, so the cost of a format is the length of the pipeline rather than
  the size of the difference.
- "Import runs in one transaction" is a property of both functions and has to be tested against each of them
  separately, forever. Each copy looks short and correct on its own, which is why the duplication survives
  review.

## Better

```typescript
type Row = Record<string, string | undefined>;
type Parse = (text: string) => Row[];

/** The skeleton, written once; the one step that varies is a parameter. */
export async function importFile(path: string, parse: Parse): Promise<number> {
  const valid = parse(await readFile(path, "utf8")).filter((r) => r.id);
  await db.transaction(async (tx) => {
    for (const record of valid) await tx.upsert("items", record);
  });
  log.info(`imported ${valid.length} from ${path}`);
  return valid.length;
}

export const parseJson: Parse = (text) => JSON.parse(text).items;

export const parseCsv: Parse = (text) => {
  const [header, ...rows] = text.trim().split("\n").map((line) => line.split(","));
  return rows.map((row) => Object.fromEntries(header.map((h, i) => [h, row[i]])));
};

await importFile("items.csv", parseCsv);
```

A new format is a `Parse` function, a fix to the pipeline lands in every importer at once, and the transaction
property is tested once with a fake parser. When several steps vary together, an `abstract class` with a
`run` method and `protected abstract` hooks is the same skeleton in its classic form.
