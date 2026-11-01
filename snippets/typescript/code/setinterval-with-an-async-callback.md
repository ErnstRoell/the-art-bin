---
aliases: [async-setinterval, overlapping-interval]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: concurrency
tags: [async, timers, polling, javascript]
keywords: ["setInterval(async", "setInterval(", "await", "clearInterval"]
signature: "setInterval is given an async callback, which it fires on schedule without waiting for the previous run, so a slow run overlaps the next one and its rejections are unhandled."
distinguish: "Fine when the callback is synchronous and quick, or when the loop awaits each run before scheduling the next with setTimeout or an awaited sleep."
added: 2026-09-30
source: MDN
---

# setInterval with an async callback

## Smell

```typescript
setInterval(async () => {
  const jobs = await queue.claimPending();
  for (const job of jobs) {
    await runJob(job);
  }
}, 5_000);
```

## Why it's bad

- `setInterval` does nothing with the promise the callback returns. When a batch takes longer than five
  seconds, the next tick starts anyway and the two runs work the queue at the same time.
- It works in development, where batches are small and fast, and turns into duplicate processing and piled-up
  requests under production load; MDN warns that slow polling with `setInterval` leaves queued requests that
  do not return in order.
- A rejection from `claimPending` or `runJob` escapes the callback as an unhandled rejection, and the interval
  keeps firing. typescript-eslint's `no-misused-promises` flags an async function passed where a void callback
  is expected.

## Better

```typescript
async function pollQueue(): Promise<void> {
  try {
    for (const job of await queue.claimPending()) {
      await runJob(job);
    }
  } catch (err) {
    log.error("poll failed", err);
  }
  setTimeout(pollQueue, 5_000);
}

void pollQueue();
```

MDN recommends this recursive `setTimeout` pattern: it does not keep a fixed rate, but it guarantees the
previous run has finished before the next one starts.
