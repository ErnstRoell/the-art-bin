---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: naming
tags: [identifiers, abbreviations]
keywords: ["let res =", "let resp =", "let cfg =", "let val =", "let tmp =", "let mgr ="]
signature: "Bindings are clipped to abbreviations such as res, cfg, val or mgr, so the reader has to decode what each one holds."
distinguish: "Fine for names that are the community's own vocabulary, such as buf, fmt, ctx, tx and rx, or a closure parameter whose scope is a single line."
added: 2026-09-23
source: jeremy-wayland
---

# Abbreviated binding name

## Smell

```rust
pub async fn sync(cli: &Client, cfg: &Cfg) -> Result<usize, SyncError> {
    let res = cli.get(&cfg.src_url).send().await?;
    let val: Vec<Rec> = res.json().await?;
    let mut cnt = 0;
    for r in val {
        if r.upd > cfg.ts {
            cnt += 1;
        }
    }
    Ok(cnt)
}
```

## Why it's bad

- `res` could be a `Result`, a response or a resource, and in Rust all three are common. The type is visible
  only in an editor with inlay hints, not in a diff or a review.
- `val`, `r`, `upd` and `ts` each need a lookup, so a ten-line function takes a minute to read.
- Rust's type inference already removes most annotations from the page. The name is often the only thing
  left saying what a value is.

## Better

```rust
pub async fn count_updated(client: &Client, config: &SyncConfig) -> Result<usize, SyncError> {
    let response = client.get(&config.source_url).send().await?;
    let records: Vec<Record> = response.json().await?;
    Ok(records.iter().filter(|record| record.updated_at > config.last_synced).count())
}
```
