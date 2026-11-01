---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [bridge, generics, composition, combinatorial-explosion]
keywords: ["struct PdfToS3", "struct CsvToS3", "struct PdfToEmail", "impl Exporter for", "ToS3", "ToEmail"]
signature: "One family of types varies along two independent axes at once, so the number of types is the product of the two lists rather than their sum."
distinguish: "Fine when the combinations are few, fixed, and genuinely need behaviour that neither axis alone could express."
added: 2026-09-23
source: refactoring.guru
---

# Type per combination of two axes

## Smell

```rust
pub trait Exporter {
    fn export(&self, report: &Report) -> Result<(), ExportError>;
}

pub struct PdfToS3 { bucket: String }
pub struct PdfToEmail { to: String }
pub struct CsvToS3 { bucket: String }
pub struct CsvToEmail { to: String }

impl Exporter for PdfToS3 {
    fn export(&self, report: &Report) -> Result<(), ExportError> {
        let bytes = render_pdf(report)?;
        s3_put(&self.bucket, &format!("{}.pdf", report.id), &bytes)
    }
}

impl Exporter for PdfToEmail {
    fn export(&self, report: &Report) -> Result<(), ExportError> {
        let bytes = render_pdf(report)?;
        send_mail(&self.to, "report.pdf", &bytes)
    }
}

impl Exporter for CsvToS3 {
    fn export(&self, report: &Report) -> Result<(), ExportError> {
        let bytes = render_csv(report)?;
        s3_put(&self.bucket, &format!("{}.csv", report.id), &bytes)
    }
}

// CsvToEmail is the same again, and XLSX or SFTP adds a whole row or column
```

## Why it's bad

- Two formats and two destinations are four types; adding XLSX and SFTP makes nine. Each new value on either
  axis multiplies the work.
- Each type duplicates one line from each axis, so a fix to how PDFs are rendered or how S3 keys are named has
  to be applied to every type in its row or column.
- A missing combination is a missing type, discovered when someone asks for CSV by email and finds nothing.

## Better

```rust
pub trait Format {
    fn render(&self, report: &Report) -> Result<Vec<u8>, ExportError>;
    fn extension(&self) -> &'static str;
}

pub trait Destination {
    fn deliver(&self, name: &str, bytes: &[u8]) -> Result<(), ExportError>;
}

pub struct Exporter<F, D> {
    format: F,
    destination: D,
}

impl<F: Format, D: Destination> Exporter<F, D> {
    pub fn export(&self, report: &Report) -> Result<(), ExportError> {
        let bytes = self.format.render(report)?;
        self.destination.deliver(&format!("{}.{}", report.id, self.format.extension()), &bytes)
    }
}

// Exporter { format: Pdf, destination: S3 { bucket } }
// Exporter { format: Csv, destination: Email { to } }
```

Each axis is its own trait, and the combinations are assembled rather than written. Two formats and two
destinations are four types, and adding one more of each makes six.
