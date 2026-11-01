---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: strings
tags: [utf-8, osstr, paths, encoding]
keywords: [".to_string_lossy()", "from_utf8_lossy(", ".display().to_string()", ".into_string().unwrap()", "OsString"]
signature: "A path, OS string or byte buffer is converted to a String lossily and then used to address the original, so any non-UTF-8 byte is replaced and the result names something else."
distinguish: "Fine when the lossy string is only shown to a human, such as in a log line or an error message, and never fed back into the filesystem or the protocol."
added: 2026-09-23
source: jeremy-wayland
---

# Lossy conversion of a path that round-trips

## Smell

```rust
pub fn purge_temp(dir: &Path) -> std::io::Result<()> {
    for entry in std::fs::read_dir(dir)? {
        let name = entry?.file_name().to_string_lossy().to_string();
        if name.ends_with(".tmp") {
            std::fs::remove_file(dir.join(&name))?;
        }
    }
    Ok(())
}
```

## Why it's bad

- Unix file names are bytes and Windows ones are UTF-16 that may be unpaired. `to_string_lossy` replaces
  anything invalid with U+FFFD, so `dir.join(&name)` names a file that is not the one listed.
- `remove_file` then fails with not-found and the `?` aborts the whole purge, so one oddly named file stops
  every later file from being cleaned up.
- The conversion is invisible in testing, because every fixture name is ASCII. It surfaces on a user's
  machine with a file copied from an old Windows share.

## Better

```rust
pub fn purge_temp(dir: &Path) -> std::io::Result<()> {
    for entry in std::fs::read_dir(dir)? {
        let path = entry?.path();
        if path.extension() == Some(OsStr::new("tmp")) {
            std::fs::remove_file(&path)?;
        }
    }
    Ok(())
}
```
