---
aliases: [wall-clock-for-durations]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: stdlib-misuse
tags: [time, clocks, metrics, monotonic, javascript]
keywords: ["Date.now() - start", "const start = Date.now()", "new Date().getTime()", "Date.now() -"]
signature: "An elapsed duration is measured by subtracting two Date.now readings, which come from the adjustable wall clock rather than a monotonic one."
distinguish: "Fine when the timestamps must mean wall-clock time, such as an expiry stored in a database or compared across processes, where a monotonic clock's origin is meaningless."
added: 2026-09-30
source: MDN
---

# Date.now used for elapsed time

## Smell

```typescript
async function timed<T>(label: string, work: () => Promise<T>): Promise<T> {
  const start = Date.now();
  const result = await work();
  metrics.histogram(label, Date.now() - start);
  return result;
}
```

## Why it's bad

- `Date.now()` reads the system clock, which moves with NTP corrections, clock skew and manual changes. An
  adjustment between the two readings produces a negative or inflated duration.
- It has one-millisecond resolution, so fast operations record as `0` and latency histograms lose their low
  end.
- It works on a developer laptop and presents in production as occasional impossible values, such as negative
  latencies, around clock synchronisation.

## Better

```typescript
async function timed<T>(label: string, work: () => Promise<T>): Promise<T> {
  const start = performance.now(); // monotonic, in browsers, workers and Node.js
  const result = await work();
  metrics.histogram(label, performance.now() - start);
  return result;
}
```
