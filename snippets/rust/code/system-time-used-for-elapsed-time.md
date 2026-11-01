---
aliases: []
language: rust
rust: ">=1.8"
severity: trap
category: correctness
topic: stdlib-misuse
tags: [time, clocks, monotonic, durations]
keywords: ["SystemTime::now()", ".duration_since(start)", ".elapsed().unwrap()", "UNIX_EPOCH", "Utc::now() -"]
signature: "A duration is measured by subtracting two SystemTime readings, which the wall clock can move between, instead of using the monotonic Instant."
distinguish: "Fine when the question is about calendar time, such as how old a file's modification time is, where wall-clock time is the thing being compared."
added: 2026-09-23
source: jeremy-wayland
---

# SystemTime used for elapsed time

## Smell

```rust
pub fn timed<T>(label: &str, work: impl FnOnce() -> T) -> T {
    let start = SystemTime::now();
    let result = work();
    let took = SystemTime::now().duration_since(start).unwrap();
    log::info!("{label} took {took:?}");
    result
}
```

## Why it's bad

- NTP, a manual clock change or a VM resuming can move the wall clock backwards between the two readings,
  and `duration_since` then returns `Err`, which the `unwrap` turns into a panic after the work succeeded.
- A forward step makes the operation look minutes long, which trips timeouts and ruins latency metrics.
- It fails rarely and only on real machines, so it presents as an unreproducible panic in a timing helper.

## Better

```rust
pub fn timed<T>(label: &str, work: impl FnOnce() -> T) -> T {
    let start = Instant::now();
    let result = work();
    log::info!("{label} took {:?}", start.elapsed());
    result
}
```
