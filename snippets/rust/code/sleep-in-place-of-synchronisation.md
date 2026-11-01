---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: testability
topic: concurrency
tags: [testing, flaky, timing, synchronisation]
keywords: ["thread::sleep(", "tokio::time::sleep(", "Duration::from_millis(", "Duration::from_secs(", "// wait for"]
signature: "A fixed sleep stands in for waiting on a condition, such as a server becoming ready or a worker finishing, so correctness depends on how fast the machine is."
distinguish: "Fine when the delay is itself the behaviour, such as a backoff between retries or a rate limit, rather than a guess at how long something else takes."
added: 2026-09-23
source: jeremy-wayland
---

# Sleep in place of synchronisation

## Smell

```rust
#[test]
fn worker_processes_queued_job() {
    let queue = Queue::new();
    let worker = std::thread::spawn({
        let queue = queue.clone();
        move || run_worker(queue)
    });
    queue.push(Job::new("resize"));
    std::thread::sleep(std::time::Duration::from_millis(200)); // wait for the worker
    assert_eq!(queue.completed(), 1);
}
```

## Why it's bad

- 200 ms is a guess. On a loaded CI runner the worker has not finished and the test fails; on a fast laptop
  it finished in 2 ms and the test wasted the rest.
- The usual fix for a flake is a larger number, so suites drift towards many seconds of sleeping while still
  failing occasionally.
- The sleep hides what the test is actually waiting for, so a reader cannot tell which event the assertion
  depends on.

## Better

```rust
#[test]
fn worker_processes_queued_job() {
    let queue = Queue::new();
    let (done_tx, done_rx) = std::sync::mpsc::channel();
    std::thread::spawn({
        let queue = queue.clone();
        move || run_worker_notifying(queue, done_tx)
    });
    queue.push(Job::new("resize"));
    let finished = done_rx.recv_timeout(std::time::Duration::from_secs(5)).expect("worker never finished");
    assert_eq!(finished.name, "resize");
}
```
