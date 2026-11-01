---
aliases: [snowflake-id-as-number, int64-id-in-json]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: numerics
tags: [json, precision, ids, bigint, javascript]
keywords: ["id: number", "userId: number", "JSON.parse(", "res.json()", "Number(id)", "parseInt(id"]
signature: "A 64-bit integer id arrives as a JSON number and is parsed into a JavaScript number, which rounds any value above Number.MAX_SAFE_INTEGER to a different id."
distinguish: "Fine for integer ids guaranteed to stay below Number.MAX_SAFE_INTEGER, such as auto-increment keys in a small table, or when the API already sends the id as a JSON string."
added: 2026-09-30
source: MDN
---

# Large integer id parsed as number

## Smell

```typescript
interface Tweet {
  id: number;
  text: string;
}

async function likeTweet(url: string): Promise<void> {
  // response body: {"id": 1234567890123456789, "text": "hi"}
  const tweet = (await (await fetch(url)).json()) as Tweet;
  await fetch(`/api/tweets/${tweet.id}/like`, { method: "POST" });
  // POST /api/tweets/1234567890123456800/like
}
```

## Why it's bad

- `JSON.parse` turns every JSON number into a double. Integers above `Number.MAX_SAFE_INTEGER`
  (`2 ** 53 - 1`) cannot all be represented, so `1234567890123456789` becomes `1234567890123456800`.
- The precision is gone before any reviver runs, so fixing it after parsing is not possible with a plain
  reviver.
- 64-bit ids from databases routinely exceed the limit, and the rounded value is still
  a plausible id: the request goes to the wrong record or a missing one, with no error at the parse.

## Better

```typescript
interface Tweet {
  id: string; // the API sends ids as JSON strings; use BigInt(id) if arithmetic is needed
  text: string;
}

async function likeTweet(url: string): Promise<void> {
  const tweet = (await (await fetch(url)).json()) as Tweet;
  await fetch(`/api/tweets/${tweet.id}/like`, { method: "POST" });
}
```
