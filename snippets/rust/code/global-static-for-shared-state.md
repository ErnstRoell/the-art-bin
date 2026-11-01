---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: testability
topic: mutability
tags: [global-state, statics, caching, testing]
keywords: ["static mut", "static CACHE", "LazyLock<Mutex<", "OnceLock<", "lazy_static!", "thread_local!"]
signature: "A function keeps cache or configuration in a process-wide static, so its result depends on what ran before it in the same process."
distinguish: "Fine for values that are computed once and never change afterwards, such as a compiled regex or a lookup table, where every caller would build the same thing."
added: 2026-09-23
source: jeremy-wayland
---

# Global static for shared state

## Smell

```rust
static RATES: LazyLock<Mutex<HashMap<String, f64>>> = LazyLock::new(Default::default);

pub fn convert(amount: f64, currency: &str) -> Result<f64, FxError> {
    let mut rates = RATES.lock().unwrap();
    if !rates.contains_key(currency) {
        rates.insert(currency.to_owned(), fetch_rate(currency)?);
    }
    Ok(amount * rates[currency])
}
```

## Why it's bad

- `cargo test` runs tests as threads in one process, so a test that seeds a rate leaks it into every test that
  runs after it. Tests pass alone and fail together, or the reverse, depending on scheduling.
- There is no way to give one caller a different rate source or an empty cache; the only seam is the network
  call hidden inside `fetch_rate`.
- The cache never expires and has no owner, so "why is this rate stale" has no answer short of restarting the
  process.

## Better

```rust
pub struct Rates<S> {
    source: S,
    cache: Mutex<HashMap<String, f64>>,
}

impl<S: RateSource> Rates<S> {
    pub fn convert(&self, amount: f64, currency: &str) -> Result<f64, FxError> {
        let mut cache = self.cache.lock().unwrap();
        if let Some(rate) = cache.get(currency) {
            return Ok(amount * rate);
        }
        let rate = self.source.fetch(currency)?;
        cache.insert(currency.to_owned(), rate);
        Ok(amount * rate)
    }
}
```

The owner constructs one `Rates` and passes it down; each test constructs its own with a fake source.
