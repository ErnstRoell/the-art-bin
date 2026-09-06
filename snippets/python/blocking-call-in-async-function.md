---
aliases: [sync-call-in-coroutine, blocked-event-loop]
language: python
python: ">=3.5"
severity: trap
category: performance
topic: concurrency
tags: [asyncio, event-loop, blocking]
keywords: ["async def", "requests.get", "time.sleep", "await", "run_in_executor"]
signature: "An async function calls a blocking library or time.sleep, so the event loop stops until that call returns."
distinguish: "Fine when the blocking call is handed to a thread or process executor, which keeps the loop free to run other tasks."
added: 2026-09-04
source: ernst
---

# Blocking call inside an async function

## Smell

```python
async def fetch_all(urls):
    results = []
    for url in urls:
        results.append(requests.get(url).json())
        time.sleep(0.1)
    return results
```

## Why it's bad

- A coroutine only yields control at an `await`. There is none here, so `fetch_all` holds the event loop for
  the whole duration and no other task — including timers, health checks, and cancellation — can run.
- The concurrency is therefore entirely notional: gathering a hundred of these coroutines takes the same time
  as calling them one after another, plus overhead.
- It is invisible in tests that exercise one request at a time, and appears only under load, as latency that
  scales with total traffic rather than with per-request work.
- `time.sleep` is the clearest tell, since `asyncio.sleep` exists precisely to express the same intent without
  holding the loop.

## Better

```python
async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*(client.get(url) for url in urls))
    return [response.json() for response in responses]
```
