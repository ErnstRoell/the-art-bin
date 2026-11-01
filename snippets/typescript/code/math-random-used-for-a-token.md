---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: stdlib-misuse
tags: [randomness, tokens, crypto, session, javascript]
keywords: ["Math.random()", "Math.random().toString(36)", ".toString(36).slice(2)", "Math.floor(Math.random() *", "token", "nonce"]
signature: "A token, session id, password reset code or nonce is generated with Math.random, which is not a cryptographically secure generator."
distinguish: "Fine for values with no security meaning, such as retry jitter, sampling, shuffling a quiz or picking a placeholder colour."
added: 2026-09-30
source: MDN
---

# Math.random used for a token

## Smell

```typescript
export function createResetToken(): string {
  let token = "";
  for (let i = 0; i < 32; i++) {
    token += Math.floor(Math.random() * 36).toString(36);
  }
  return token;
}

export const newSessionId = () => Math.random().toString(36).slice(2);
```

## Why it's bad

- MDN is explicit that `Math.random()` does not provide cryptographically secure numbers and must not be used
  for anything related to security; a guessable reset token is an account takeover.
- The token looks long and random in logs and in review, which is why this survives: 32 characters of output
  say nothing about how predictable the generator behind them is.
- The `toString(36).slice(2)` idiom is also shorter than it looks and varies in length.

## Better

```typescript
import { randomBytes, randomUUID } from "node:crypto";

export function createResetToken(): string {
  return randomBytes(32).toString("base64url");
}

// in the browser, crypto.randomUUID() and crypto.getRandomValues() are the equivalents
export const newSessionId = () => randomUUID();
```
