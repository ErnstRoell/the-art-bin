---
aliases: [sleep-in-test, time-sleep-synchronisation]
language: python
python: ">=3.0"
severity: trap
category: testability
topic: concurrency
tags: [flaky, timing, synchronisation]
keywords: ["time.sleep", "sleep(", "asyncio.sleep", "await asyncio.sleep"]
signature: "A fixed sleep stands in for waiting on a condition to become true."
distinguish: "Fine when the delay is the behaviour under test, such as backoff or rate limiting, rather than a stand-in for waiting."
added: 2026-09-04
source: ernst
---

# Sleep used to await a condition

## Smell

```python
def test_worker_processes_the_job(queue):
    job = queue.submit(build_job())
    time.sleep(2)
    assert job.done
```

## Why it's bad

- The duration encodes a guess about machine speed, so the test passes locally and fails on a loaded CI runner.
- Every sleep is paid in full even when the condition was met immediately, so the suite gets slower as it grows.
- The real synchronisation point is never named, so nobody can tell what the test is actually waiting for.
- Failures look like flakiness rather than a missing wait, so the usual fix is a longer sleep.

## Better

```python
def test_worker_processes_the_job(queue):
    job = queue.submit(build_job())
    wait_until(lambda: job.done, timeout=5)
    assert job.done
```
