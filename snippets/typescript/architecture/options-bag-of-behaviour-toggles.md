---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: functions
tags: [decorator, composition, higher-order-functions, boolean-options]
keywords: ["retry?: boolean", "cache?: boolean", "log?: boolean", "if (opts.retry)", "if (options.", "{ retry: true, cache: true }"]
signature: "A function takes an options object of boolean toggles for independent optional behaviours, so its body interleaves all of them and the number of paths through it doubles with each flag."
distinguish: "Fine when the options are settings for the one behaviour the function performs, such as a timeout or an encoding, rather than separate behaviours layered on top of it."
added: 2026-09-30
source: refactoring.guru
---

# Options bag of behaviour toggles

## Smell

```typescript
interface FetchOptions {
  retry?: boolean;
  cache?: boolean;
  log?: boolean;
}

const cache = new Map<string, unknown>();

export async function fetchJson(url: string, opts: FetchOptions = {}): Promise<unknown> {
  if (opts.cache && cache.has(url)) return cache.get(url);
  if (opts.log) console.info("GET", url);
  let attempts = opts.retry ? 3 : 1;
  let body: unknown;
  while (attempts-- > 0) {
    try {
      const res = await fetch(url);
      body = await res.json();
      break;
    } catch (err) {
      if (opts.log) console.warn("retrying", url, err);
      if (attempts === 0) throw err;
    }
  }
  if (opts.cache) cache.set(url, body);
  return body;
}

// fetchJson(PRICES, { retry: true, cache: true })
// fetchJson(PROFILE, { log: true })
```

## Why it's bad

- Three independent behaviours are braided into one body. Reading the retry loop means skipping over caching
  and logging, and changing the cache means being sure no retry path stores an unset `body`.
- Three flags are eight combinations, and the tests cover the two someone needed. The order between them is
  fixed inside the function, so nobody can log only cache misses without editing it.
- The behaviours are not reusable: `upload`, next month, wants retry and logging and gets them by copying these
  lines, so the retry policy ends up existing twice.
- A fourth concern, such as rate limiting, is a new flag, a new branch, and another doubling of the test matrix.

## Better

```typescript
type Fetcher = (url: string) => Promise<unknown>;

const plain: Fetcher = async (url) => (await fetch(url)).json();

const withRetry = (next: Fetcher, attempts = 3): Fetcher => async (url) => {
  for (let i = 1; ; i++) {
    try { return await next(url); } catch (err) { if (i >= attempts) throw err; }
  }
};

const withCache = (next: Fetcher, cache = new Map<string, Promise<unknown>>()): Fetcher => (url) => {
  if (!cache.has(url)) cache.set(url, next(url).catch((err) => { cache.delete(url); throw err; }));
  return cache.get(url)!;
};

const withLog = (next: Fetcher): Fetcher => (url) => (console.info("GET", url), next(url));

export const fetchPrices = withCache(withRetry(plain));
export const fetchProfile = withLog(plain);
```

Each behaviour is a function from a `Fetcher` to a `Fetcher`, the same type as what it wraps, so they compose
in whatever order the caller writes and `plain` knows none of them exist.
