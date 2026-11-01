---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: classes
tags: [builder, invariants, initialisation, options]
keywords: ["Option<", ": None,", ".unwrap()", "= Some(", "#[derive(Default)]", "report.title = Some("]
signature: "A struct is created with every field None and completed by assigning them one at a time, so every half-built value has the same type as a finished one and each use unwraps."
distinguish: "Fine when the fields are genuinely optional and independent, so a value with any of them absent is complete and valid."
added: 2026-09-23
source: refactoring.guru
---

# Struct with Option fields filled in later

## Smell

```rust
#[derive(Default)]
pub struct Report {
    pub title: Option<String>,
    pub rows: Option<Vec<Row>>,
    pub total: Option<Money>,
    pub footer: Option<String>,
}

impl Report {
    pub fn render(&self) -> String {
        format!(
            "{}\n{:?}\n{}\n{}",
            self.title.as_ref().unwrap(),
            self.rows.as_ref().unwrap(),
            self.total.unwrap(),
            self.footer.as_deref().unwrap_or(""),
        )
    }
}

pub fn preview(rows: &[Row]) -> String {
    let mut report = Report::default();
    report.title = Some("Preview".into());
    report.rows = Some(rows[..5].to_vec());
    report.render()          // panics: total was never set
}
```

## Why it's bad

- `Option` is how Rust says a value may legitimately be absent. Here it means "not assigned yet", so the type
  cannot tell a finished report from one mid-construction, and `render` unwraps its way through the difference.
- The construction order is a contract kept in the head of whoever wrote the first call site. `preview` breaks
  it and panics at runtime, where a missing constructor argument would not have compiled.
- `#[derive(Default)]` makes the empty, invalid report the easiest one to create.

## Better

```rust
pub struct Report {
    title: String,
    rows: Vec<Row>,
    total: Money,
    footer: String,
}

pub struct ReportBuilder {
    title: String,
    footer: String,
}

impl ReportBuilder {
    pub fn new(title: impl Into<String>) -> Self {
        Self { title: title.into(), footer: String::new() }
    }

    pub fn confidential(mut self) -> Self {
        self.footer = "confidential".into();
        self
    }

    pub fn build(self, rows: Vec<Row>) -> Report {
        let total = rows.iter().map(|row| row.amount).sum();
        Report { title: self.title, rows, total, footer: self.footer }
    }
}

pub fn preview(rows: &[Row]) -> String {
    ReportBuilder::new("Preview").build(rows.iter().take(5).cloned().collect()).render()
}
```

Optional settings live in the builder, required inputs are arguments to `build`, and a `Report` that exists is
finished, so `render` has nothing to unwrap.
