---
aliases: []
language: rust
rust: ">=1.39"
severity: trap
category: correctness
topic: concurrency
tags: [async, mutex, deadlock, tokio]
keywords: [".lock().await", ".lock().unwrap()", "MutexGuard", ".await", "RwLock", "current_thread"]
signature: "A mutex guard is still alive when the task reaches an await, so the lock is held while the task is suspended and every other task that wants it stalls or deadlocks."
distinguish: "Fine when the guard is dropped before the await, or when the lock is an async mutex deliberately held to serialise the awaited operation itself."
added: 2026-09-23
source: jeremy-wayland
---

# Lock guard held across await

## Smell

```rust
async fn record_visit(state: &AppState, user: UserId) -> Result<(), AppError> {
    let mut visits = state.visits.lock().await;
    let profile = state.db.load_profile(user).await?;   // lock held for a database round trip
    *visits.entry(profile.region).or_insert(0) += 1;
    state.audit.write(&profile).await?;                 // and for a second one
    Ok(())
}
```

## Why it's bad

- The guard lives until the end of the scope, so the lock is held across two network waits. Every request
  that touches `visits` queues behind them and throughput collapses to one at a time.
- With `std::sync::Mutex` the same shape is worse. Under `tokio::spawn` it fails to compile only because the
  guard is not `Send`; where no `Send` bound applies, such as `spawn_local` or a future awaited directly on a
  `current_thread` runtime, it compiles and deadlocks the first time another task on that thread tries to lock.
- Nothing about the code looks slow. The lock is a line above the await, and the cost appears only under
  concurrent load.

## Better

```rust
async fn record_visit(state: &AppState, user: UserId) -> Result<(), AppError> {
    let profile = state.db.load_profile(user).await?;
    {
        let mut visits = state.visits.lock().await;
        *visits.entry(profile.region).or_insert(0) += 1;
    } // guard dropped before the next await
    state.audit.write(&profile).await?;
    Ok(())
}
```
