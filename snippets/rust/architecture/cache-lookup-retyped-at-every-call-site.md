---
aliases: []
language: rust
rust: ">=1.75"
severity: trap
category: correctness
topic: classes
tags: [proxy, caching, traits, wrappers]
keywords: ["cache.get(&key)", "cache.insert(key", "if let Some(cached) =", "format!(\"user:{}\"", "Instant::now() - ", "fetch_user("]
signature: "The check-cache, fetch, store sequence around an expensive call is retyped at every call site, so key layout, expiry and invalidation are decided independently in each one."
distinguish: "Fine when there is exactly one call site and the caching is a local optimisation of that one function."
added: 2026-09-23
source: refactoring.guru
---

# Cache lookup retyped at every call site

## Smell

```rust
pub async fn profile_page(state: &AppState, id: UserId) -> Result<Html, AppError> {
    let key = format!("user:{id}");
    let user = match state.cache.lock().unwrap().get(&key).cloned() {
        Some((user, at)) if at.elapsed() < Duration::from_secs(60) => user,
        _ => {
            let user = state.api.fetch_user(id).await?;
            state.cache.lock().unwrap().insert(key, (user.clone(), Instant::now()));
            user
        }
    };
    Ok(render_profile(&user))
}

pub async fn invoice_pdf(state: &AppState, id: UserId) -> Result<Vec<u8>, AppError> {
    let key = format!("users/{id}");                       // different key layout
    let user = match state.cache.lock().unwrap().get(&key).cloned() {
        Some((user, _)) => user,                           // never expires
        None => {
            let user = state.api.fetch_user(id).await?;
            state.cache.lock().unwrap().insert(key, (user.clone(), Instant::now()));
            user
        }
    };
    Ok(render_invoice(&user))
}
```

## Why it's bad

- Two call sites, two key formats, two expiry policies. Updating a user's address and invalidating
  `user:{id}` leaves the stale entry under `users/{id}`, so invoices go to the old address.
- Every caller has to remember the locking, the clone and the timestamp, and one of them eventually forgets
  one.
- There is no single place to add metrics, change the TTL or swap the cache for Redis; each is a hunt through
  every handler.

## Better

```rust
pub trait UserSource {
    async fn user(&self, id: UserId) -> Result<User, AppError>;
}

pub struct CachedUsers<S> {
    inner: S,
    ttl: Duration,
    entries: Mutex<HashMap<UserId, (User, Instant)>>,
}

impl<S: UserSource> UserSource for CachedUsers<S> {
    async fn user(&self, id: UserId) -> Result<User, AppError> {
        if let Some((user, at)) = self.entries.lock().unwrap().get(&id) {
            if at.elapsed() < self.ttl {
                return Ok(user.clone());
            }
        }
        let user = self.inner.user(id).await?;
        self.entries.lock().unwrap().insert(id, (user.clone(), Instant::now()));
        Ok(user)
    }
}

// handlers call state.users.user(id).await and never see the cache
```

The wrapper has the same interface as what it wraps, so callers cannot tell and cannot get the policy wrong.
