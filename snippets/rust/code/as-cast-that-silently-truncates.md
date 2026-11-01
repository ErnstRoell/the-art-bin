---
aliases: []
language: rust
rust: ">=1.34"
severity: trap
category: correctness
topic: numerics
tags: [casts, overflow, integers]
keywords: [" as u8", " as u16", " as u32", " as i32", " as usize", "as u64 as"]
signature: "A numeric value that can be out of range is converted with as, so it wraps, truncates or saturates without any error."
distinguish: "Fine when the conversion is widening and cannot lose information, such as u32 as u64, or when wrapping is the intended arithmetic, such as hashing."
added: 2026-09-23
source: jeremy-wayland
---

# As cast that silently truncates

## Smell

```rust
pub fn listen_port(config: &Config) -> u16 {
    config.port as u16          // config.port: i64, read from a file
}

pub fn chunk_count(len: usize) -> u32 {
    (len / CHUNK) as u32
}
```

## Why it's bad

- `as` between integers never fails: `70000_i64 as u16` is `4464` and `-1_i64 as u16` is `65535`. A typo in
  a config file becomes a service listening on a different, valid port.
- `usize as u32` is fine on a laptop's test data and truncates on a large enough input, so the bug waits for
  production volume.
- Float casts saturate and send NaN to zero, so `f64 as u32` turns garbage into a plausible number too.

## Better

```rust
pub fn listen_port(config: &Config) -> Result<u16, ConfigError> {
    u16::try_from(config.port).map_err(|_| ConfigError::PortOutOfRange(config.port))
}

pub fn chunk_count(len: usize) -> Result<u32, std::num::TryFromIntError> {
    u32::try_from(len / CHUNK)
}
```
