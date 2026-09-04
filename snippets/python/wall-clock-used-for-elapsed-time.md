---
aliases: [time-time-for-duration, non-monotonic-timing]
language: python
python: ">=3.3"
severity: trap
category: correctness
topic: stdlib-misuse
tags: [timing, monotonic, benchmarks]
keywords: ["time.time()", "start = time.time", "elapsed", "time.monotonic", "perf_counter"]
signature: "A duration is measured by subtracting two time.time readings, which the system clock can move between."
distinguish: "Fine when the value being recorded is an absolute timestamp for a log or a database rather than an interval."
added: 2026-09-04
source: ernst
---

# Wall clock used to measure elapsed time

## Smell

```python
def timed(fn, *args):
    start = time.time()
    result = fn(*args)
    return result, time.time() - start
```

## Why it's bad

- `time.time()` reads the system clock, which is not guaranteed to advance monotonically: NTP corrections,
  manual changes, and suspend or resume can move it backwards or forwards mid-measurement.
- A backward step produces a negative duration, which then propagates into averages, rate calculations, and
  timeout arithmetic as a plausible number with the wrong sign.
- Its resolution is also worse than `perf_counter` on some platforms, so short measurements are noisier than
  they need to be even when the clock behaves.
- It presents as a benchmark with an impossible outlier, or a long-running job whose reported throughput jumps
  once a day — right after the clock is synchronised.

## Better

```python
def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start
```
