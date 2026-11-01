---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: performance
topic: strings
tags: [logging, formatting, laziness]
keywords: ['let msg = format!(', 'debug!("{}", msg)', 'format!("{:#?}"', "trace!(\"{}\",", "log_enabled!("]
signature: "A log message is built with format before the log macro is called, so the work is done even when that level is switched off."
distinguish: "Fine when the arguments are passed straight to the log macro, which only formats them if the level is enabled, or when the string is needed for something besides the log."
added: 2026-09-23
source: jeremy-wayland
---

# Log message formatted before the log call

## Smell

```rust
pub fn apply(batch: &Batch) -> Result<(), ApplyError> {
    let summary = format!("applying batch {:#?}", batch); // pretty-prints every row
    log::debug!("{}", summary);
    batch.rows.iter().try_for_each(apply_row)
}
```

## Why it's bad

- The `log` and `tracing` macros check the level before evaluating their arguments. Formatting outside the
  macro defeats that, so production pays for a pretty-printed dump of every batch that nobody logs.
- `{:#?}` over a large batch is not cheap: it allocates proportionally to the data, on every call, on the hot
  path.
- The intermediate binding reads as though `summary` is used for something else, so a reader goes looking.

## Better

```rust
pub fn apply(batch: &Batch) -> Result<(), ApplyError> {
    log::debug!("applying batch {} with {} rows", batch.id, batch.rows.len());
    log::trace!("batch contents: {:#?}", batch); // formatted only when trace is on
    batch.rows.iter().try_for_each(apply_row)
}
```
