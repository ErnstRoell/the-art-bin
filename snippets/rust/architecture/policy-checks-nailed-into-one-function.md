---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: control-flow
tags: [chain-of-responsibility, middleware, policies]
keywords: ["return Err(Rejected::", "fn check_request(", "if !is_authenticated(", "if rate_limited(", "if req.body.len() >", "Vec<Box<dyn Check>>"]
signature: "Independent policy checks are hardcoded as a fixed sequence of early returns in one function, so no caller can add, remove or reorder them."
distinguish: "Fine when the checks are few, always apply together and are genuinely one policy that nobody configures per route."
added: 2026-09-23
source: refactoring.guru
---

# Policy checks nailed into one function

## Smell

```rust
pub fn check_request(req: &Request, state: &AppState) -> Result<(), Rejected> {
    if !state.auth.is_authenticated(req) {
        return Err(Rejected::Unauthenticated);
    }
    if state.limiter.is_limited(req.client_ip()) {
        return Err(Rejected::RateLimited);
    }
    if req.body.len() > 1_000_000 {
        return Err(Rejected::TooLarge);
    }
    if req.path.starts_with("/admin") && !state.auth.is_admin(req) {
        return Err(Rejected::Forbidden);
    }
    if state.maintenance.load(Ordering::Relaxed) {
        return Err(Rejected::Maintenance);
    }
    Ok(())
}
```

## Why it's bad

- The health-check endpoint must skip authentication and the upload endpoint needs a larger body limit. Neither
  is possible without adding special cases to this function, which is how it grows a `match req.path` inside.
- The order is fixed by the text. Rate limiting after authentication means unauthenticated floods still hit the
  auth backend, and moving one check means editing a function every route depends on.
- Each check cannot be tested alone; every test builds a request that passes all the checks before it.

## Better

```rust
pub trait Check {
    fn check(&self, req: &Request) -> Result<(), Rejected>;
}

pub struct Pipeline(Vec<Box<dyn Check + Send + Sync>>);

impl Pipeline {
    pub fn check(&self, req: &Request) -> Result<(), Rejected> {
        self.0.iter().try_for_each(|check| check.check(req))
    }
}

// Assembled per route, in the order that route needs:
let public = Pipeline(vec![Box::new(RateLimit::per_ip(100)), Box::new(MaxBody(1_000_000))]);
let uploads = Pipeline(vec![Box::new(RateLimit::per_ip(10)), Box::new(Authenticated), Box::new(MaxBody(500_000_000))]);
let admin = Pipeline(vec![Box::new(RateLimit::per_ip(100)), Box::new(Authenticated), Box::new(AdminOnly)]);
```

Each policy is a small type tested alone, and each route states its chain. This is the shape `tower` layers
take, which is worth reaching for when the service already runs on it.
