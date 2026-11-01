---
aliases: [redos]
language: typescript
typescript: ">=3.0"
severity: trap
category: security
topic: strings
tags: [redos, regex, denial-of-service, event-loop, javascript]
keywords: [")+$/", ")*$/", "+)+", "*)*", "(.+)+", "new RegExp(", ".test(req."]
signature: "A regular expression nests a quantifier inside a repeated group, so a crafted non-matching input makes the backtracking engine try exponentially many splits and stalls the event loop."
distinguish: "Fine when each repetition of the group must begin with a distinct literal, such as a dot or a comma, so any input has only one way to match, or when the pattern only ever sees trusted, length-capped strings."
added: 2026-09-30
source: OWASP ReDoS
---

# Regex open to catastrophic backtracking

## Smell

```typescript
const EMAIL = /^([a-zA-Z0-9]+\.?)+@example\.com$/;

app.post("/signup", (req, res) => {
  if (!EMAIL.test(req.body.email)) {
    return res.status(400).send("invalid email");
  }
  res.sendStatus(201);
});
```

## Why it's bad

- Because `\.?` is optional, `([a-zA-Z0-9]+\.?)+` is `(a+)+` in disguise. On a run of letters that almost ends
  in `@example.com` the engine backtracks through every way of splitting the run, and the count doubles with
  each extra character.
- Node.js runs every request on one event loop, so one slow match stalls every client of the process. On
  Node 26, 28 letters followed by `@example.co` take about 19 seconds to reject.
- Tests pass, because matching inputs and short inputs are fast. Only the near miss is slow, and nobody writes
  that test.

## Better

```typescript
// each repetition must start with a literal dot, so there is only one way to match
const EMAIL = /^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*@example\.com$/;

app.post("/signup", (req, res) => {
  const email = String(req.body.email);
  // 254 is the longest address SMTP can carry (RFC 5321 4.5.3.1.3, RFC 3696 erratum 1690)
  if (email.length > 254 || !EMAIL.test(email)) {
    return res.status(400).send("invalid email");
  }
  res.sendStatus(201);
});
```
