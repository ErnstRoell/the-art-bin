---
aliases: [missing-decorator, flag-per-optional-behaviour]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: functions
tags: [decorator, composition, boolean-parameters, wrapping]
keywords: ["retry=False", "cache=False", "verbose=False", "if log:", "if cache", "=False,"]
signature: "A function takes several boolean switches for independent optional behaviours, so its body interleaves all of them and the number of paths through it doubles with each flag."
distinguish: "Fine when one flag selects between two behaviours that share most of the body and never compose with anything else."
added: 2026-09-06
source: refactoring.guru
---

# Optional behaviour stacked as flags

## Smell

```python
_CACHE = {}


def fetch(url, retry=False, cache=False, log=False, timeout=None):
    if log:
        logger.info("fetching %s", url)
    if cache and url in _CACHE:
        return _CACHE[url]
    attempts = 3 if retry else 1
    for attempt in range(attempts):
        try:
            body = http_get(url, timeout=timeout)
            break
        except TimeoutError:
            if attempt == attempts - 1:
                raise
    if cache:
        _CACHE[url] = body
    if log:
        logger.info("fetched %s (%d bytes)", url, len(body))
    return body
```

## Why it's bad

- Three independent behaviours are braided into one body. Reading the retry logic means skipping over caching
  and logging; changing the caching means being sure the retry loop cannot leave `body` unbound on a path the
  cache then stores.
- Three booleans are eight combinations, and the tests cover the two that someone happened to need. The
  interesting one — retry on, cache on — is where a retried failure and a cache write meet, and it is the least
  likely to have been tried.
- Each new concern is an edit to a function that already does four things, plus another parameter every existing
  caller can now get wrong. `fetch(url, True, False, True)` is a real call site that eventually appears.
- The behaviours are not reusable. `download`, next month, wants retry and logging and cannot have them without
  copying these lines, so the retry policy ends up existing twice.
- This is not `boolean-parameter-selects-behaviour`, which is one flag choosing between two things a function
  might be. Here the flags do not choose; they accumulate.

## Better

```python
def with_logging(fetch):
    @wraps(fetch)
    def wrapper(url):
        logger.info("fetching %s", url)
        body = fetch(url)
        logger.info("fetched %s (%d bytes)", url, len(body))
        return body

    return wrapper


def with_retry(fetch, attempts=3):
    @wraps(fetch)
    def wrapper(url):
        for attempt in range(attempts):
            try:
                return fetch(url)
            except TimeoutError:
                if attempt == attempts - 1:
                    raise

    return wrapper


def with_cache(fetch, cache):
    @wraps(fetch)
    def wrapper(url):
        if url not in cache:
            cache[url] = fetch(url)
        return cache[url]

    return wrapper


# Composed once, where the policy belongs, and read outside-in:
fetch = with_logging(with_cache(with_retry(http_get), {}))
```

Each behaviour is a function small enough to test alone, the order is now explicit and reviewable — retry
inside the cache means failures are not cached — and `download` gets retries by wrapping, not by copying.
