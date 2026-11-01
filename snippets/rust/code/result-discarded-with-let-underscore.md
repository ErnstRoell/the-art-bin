---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: correctness
topic: exceptions
tags: [error-handling, silent-failure]
keywords: ["let _ =", ".ok();", "unwrap_or_default()", "if let Ok(", "#[must_use]"]
signature: "A Result is bound to an underscore or turned into an Option and dropped, so the error it carried is discarded without a trace."
distinguish: "Fine when failure genuinely does not matter and a comment says why, such as ignoring the send error on a channel whose receiver has already shut down."
added: 2026-09-23
source: jeremy-wayland
---

# Result discarded with let underscore

## Smell

```rust
pub fn save_settings(settings: &Settings, path: &Path) {
    let json = serde_json::to_string(settings).unwrap_or_default();
    let _ = std::fs::write(path, json);
}
```

## Why it's bad

- `let _ =` exists to silence `#[must_use]`, which is the compiler asking what should happen on failure. This
  answers "nothing" on behalf of every caller.
- `unwrap_or_default` turns a serialisation failure into an empty string, which is then written over the good
  file. The error is not only lost, it is converted into data loss.
- The function returns `()`, so callers cannot tell a saved file from a disk that was full or read-only. The
  first evidence is settings that silently reset on the next launch.

## Better

```rust
pub fn save_settings(settings: &Settings, path: &Path) -> Result<(), SettingsError> {
    let json = serde_json::to_string(settings)?;
    std::fs::write(path, json)?;
    Ok(())
}
```
