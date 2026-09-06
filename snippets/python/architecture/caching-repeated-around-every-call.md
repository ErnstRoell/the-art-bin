---
aliases: [missing-proxy, cache-aside-duplicated-per-call-site]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [proxy, caching, invalidation, boundary]
keywords: ["redis.get", "cache.get", "setex", "json.dumps", "if hit is not None", "f\"user:{"]
signature: "The check-cache-then-fetch-then-store dance around an expensive call is retyped at every call site, so key layout, expiry and invalidation are decided independently in each one."
distinguish: "Fine at a single call site with one key, where the caching is a local decision and no other code fetches the same thing."
added: 2026-09-06
source: refactoring.guru
---

# Caching repeated around every call

## Smell

```python
def profile(user_id):
    key = f"user:{user_id}"
    hit = redis.get(key)
    if hit is not None:
        return json.loads(hit)
    user = api.fetch_user(user_id)
    redis.setex(key, 300, json.dumps(user))
    return user


def badge(user_id):
    key = f"badge:{user_id}"                 # a second key for the same upstream object
    hit = redis.get(key)
    if hit is not None:
        return json.loads(hit)
    user = api.fetch_user(user_id)
    redis.setex(key, 86_400, json.dumps(user))   # and a day-long expiry, chosen here
    return user["badge"]


def rename(user_id, name):
    api.rename_user(user_id, name)
    redis.delete(f"user:{user_id}")          # invalidates one of the two keys
```

## Why it's bad

- One upstream object is cached under two keys with two lifetimes, so the program holds two answers about the
  same user and which one you get depends on which function you called.
- Invalidation can only ever be partial, because it has to know every key any call site invented. `rename`
  clears `user:` and leaves `badge:` holding the old name for a day. That is the presentation: a rename that
  "didn't work" in one part of the UI, unreproducible after the expiry.
- The next feature copies the block again, because copying is easier than finding out which key already holds
  this. The number of cache policies grows with the number of readers.
- The caching is untestable and unswitchable. There is no seam at which to disable it, so a test either runs
  against Redis or does not exercise these functions at all.

## Better

```python
class CachedUsers:
    """Proxy: same interface as the API client, so callers cannot tell it is here."""

    def __init__(self, api, cache, ttl=300):
        self._api = api
        self._cache = cache
        self._ttl = ttl

    def _key(self, user_id):
        return f"user:{user_id}"

    def fetch_user(self, user_id):
        hit = self._cache.get(self._key(user_id))
        if hit is not None:
            return json.loads(hit)
        user = self._api.fetch_user(user_id)
        self._cache.setex(self._key(user_id), self._ttl, json.dumps(user))
        return user

    def rename_user(self, user_id, name):
        self._api.rename_user(user_id, name)
        self._cache.delete(self._key(user_id))


def profile(users, user_id):
    return users.fetch_user(user_id)


def badge(users, user_id):
    return users.fetch_user(user_id)["badge"]
```

The key, the expiry and the invalidation now exist once, and because the proxy has the client's interface, a
test passes the real client to run uncached and the callers do not change.
