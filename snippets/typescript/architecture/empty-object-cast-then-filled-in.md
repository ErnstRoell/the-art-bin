---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [builder, type-assertions, invariants, initialisation]
keywords: ["{} as", "= {} as Report", "as unknown as", "report.title =", "!.", "Partial<"]
signature: "An object is created as an empty literal asserted to its finished type and completed by assigning properties one at a time, so the compiler treats every half-built value as a complete one."
distinguish: "Fine when every property is genuinely optional in the type, so a value with any of them missing is complete and valid."
added: 2026-09-30
source: refactoring.guru
---

# Empty object cast then filled in

## Smell

```typescript
interface Report {
  title: string;
  rows: Row[];
  total: number;
  footer: string;
}

function render(report: Report): string {
  return [report.title, ...report.rows.map(formatRow), `Total: ${report.total.toFixed(2)}`, report.footer]
    .join("\n");
}

export function monthly(rows: Row[]): string {
  const report = {} as Report;
  report.title = "Monthly";
  report.rows = rows;
  report.total = sum(rows);
  report.footer = "confidential";
  return render(report);
}

export function preview(rows: Row[]): string {
  const report = {} as Report;
  report.title = "Preview";
  report.rows = rows.slice(0, 5);
  return render(report);   // TypeError: cannot read properties of undefined (reading 'toFixed')
}
```

## Why it's bad

- `{} as Report` tells the compiler the object is finished before any property exists. Every required field is
  now unchecked, so `preview` compiles and crashes at runtime on the `total` it never set.
- The construction order is a contract kept in the head of whoever wrote `monthly`. A field added to `Report`
  later is missing from every such call site, and none of them fail to compile.
- The same thing arrives as `Partial<Report>` passed around and then cast, or as properties declared with `!`,
  each of which switches off exactly the check that would have caught the omission.

## Better

```typescript
function buildReport(title: string, rows: Row[], options: { confidential?: boolean } = {}): Report {
  return {
    title,
    rows,
    total: sum(rows),
    footer: options.confidential ? "confidential" : "",
  };
}

export const monthly = (rows: Row[]) => render(buildReport("Monthly", rows, { confidential: true }));
export const preview = (rows: Row[]) => render(buildReport("Preview", rows.slice(0, 5)));
```

The object is written as one literal, so the compiler checks it against `Report` and a missing or new field is
an error at the one place that builds it. Optional settings are an options object; a fluent builder class is
only worth it when the construction genuinely has steps.
