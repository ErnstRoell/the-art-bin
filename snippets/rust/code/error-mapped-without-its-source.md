---
aliases: []
language: rust
rust: ">=1.30"
severity: taste
category: maintainability
topic: exceptions
tags: [error-handling, chaining, thiserror]
keywords: ["map_err(|_|", ".map_err(|_| ", "ok_or(", "Error::Io", "fn source("]
signature: "An error is translated with map_err into a new error that drops the original, so the cause is gone before anyone can report it."
distinguish: "Fine when the original is deliberately hidden as an implementation detail at a public boundary, and the new error says everything a caller can act on."
added: 2026-09-23
source: jeremy-wayland
---

# Error mapped without its source

## Smell

```rust
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("could not read config")]
    Read,
    #[error("config is not valid TOML")]
    Parse,
}

pub fn load(path: &Path) -> Result<Config, ConfigError> {
    let text = std::fs::read_to_string(path).map_err(|_| ConfigError::Read)?;
    toml::from_str(&text).map_err(|_| ConfigError::Parse)
}
```

## Why it's bad

- `|_|` throws away the `io::Error` and the TOML error, which held the only useful facts: which file, which
  permission, which line and column.
- `Error::source()` returns `None`, so `anyhow`'s `{:#}`, `tracing` and every error reporter print "config is
  not valid TOML" and stop. The user gets a sentence with nothing to fix.
- Keeping the cause costs one field and a `#[from]` or `#[source]`, which is the whole point of the error
  types this code already derives.

## Better

```rust
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("could not read config {path}")]
    Read { path: PathBuf, #[source] source: std::io::Error },
    #[error("config is not valid TOML")]
    Parse(#[from] toml::de::Error),
}

pub fn load(path: &Path) -> Result<Config, ConfigError> {
    let text = std::fs::read_to_string(path)
        .map_err(|source| ConfigError::Read { path: path.to_owned(), source })?;
    Ok(toml::from_str(&text)?)
}
```
