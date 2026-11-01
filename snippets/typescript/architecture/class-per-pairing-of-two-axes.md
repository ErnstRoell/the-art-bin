---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [bridge, composition, inheritance, combinatorial-explosion]
keywords: ["class PdfS3Exporter", "class CsvS3Exporter", "class PdfEmailExporter", "implements Exporter", "S3Exporter", "EmailExporter"]
signature: "One family of classes varies along two independent axes at once, so the number of classes is the product of the two lists rather than their sum."
distinguish: "Fine when the combinations are few and fixed, or when each one genuinely needs behaviour that neither axis alone could express."
added: 2026-09-30
source: refactoring.guru
---

# Class per pairing of two axes

## Smell

```typescript
interface Exporter {
  export(report: Report): Promise<void>;
}

class PdfS3Exporter implements Exporter {
  constructor(private bucket: string) {}
  async export(report: Report) {
    const bytes = await renderPdf(report);
    await s3.putObject({ Bucket: this.bucket, Key: `${report.id}.pdf`, Body: bytes });
  }
}

class PdfEmailExporter implements Exporter {
  constructor(private to: string) {}
  async export(report: Report) {
    const bytes = await renderPdf(report);
    await mailer.send({ to: this.to, attachments: [{ filename: "report.pdf", content: bytes }] });
  }
}

class CsvS3Exporter implements Exporter {
  constructor(private bucket: string) {}
  async export(report: Report) {
    const bytes = renderCsv(report);
    await s3.putObject({ Bucket: this.bucket, Key: `${report.id}.csv`, Body: bytes });
  }
}

// CsvEmailExporter is the same again, and XLSX or SFTP adds a whole row or column
```

## Why it's bad

- Two formats and two destinations are four classes; adding XLSX and SFTP makes nine. Each new value on either
  axis multiplies the work.
- Each class repeats one line from each axis, so a fix to PDF rendering or to how S3 keys are named has to be
  applied to every class in its row or column.
- A missing combination is a missing class, discovered when someone asks for CSV by email and finds nothing,
  with no way to tell whether that was a decision or an oversight.

## Better

```typescript
interface Format {
  extension: string;
  render(report: Report): Promise<Uint8Array>;
}

type Destination = (filename: string, bytes: Uint8Array) => Promise<void>;

export const pdf: Format = { extension: "pdf", render: renderPdf };
export const csv: Format = { extension: "csv", render: async (report) => renderCsv(report) };

export const toS3 = (bucket: string): Destination => (filename, bytes) =>
  s3.putObject({ Bucket: bucket, Key: filename, Body: bytes }).then(() => {});
export const byEmail = (to: string): Destination => (filename, content) =>
  mailer.send({ to, attachments: [{ filename, content }] });

export async function exportReport(report: Report, format: Format, deliver: Destination) {
  await deliver(`${report.id}.${format.extension}`, await format.render(report));
}

// exportReport(report, pdf, toS3(bucket))
// exportReport(report, csv, byEmail(to))
```

Each axis is its own small type and the combinations are assembled at the call rather than written as classes.
A destination with one method is just a function type, which is the lightest bridge TypeScript offers.
