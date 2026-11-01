---
aliases: [unawaited-async-assertion, floating-expect]
language: typescript
typescript: ">=3.0"
severity: bug
category: testability
topic: exceptions
tags: [jest, vitest, testing, async, javascript]
keywords: ["expect(", ".rejects.", ".resolves.", ".rejects.toThrow", "valid-expect"]
signature: "An expect with rejects or resolves is neither awaited nor returned, so the test finishes before the assertion runs and passes whatever the promise does."
distinguish: "Fine when the assertion is awaited or returned from the test function."
added: 2026-09-30
source: Jest docs
---

# expect rejects without await

## Smell

```typescript
test("rejects an expired token", () => {
  const token = makeToken({ expiresAt: yesterday() });

  expect(verify(token)).rejects.toThrow(TokenExpiredError);
});
```

## Why it's bad

- `.rejects` makes the assertion itself a promise. Jest's docs warn that if it is not returned, the test
  completes before the promise is settled and the matcher has a chance to run.
- The test goes green even if `verify` accepts expired tokens, so the suite reports coverage of a security
  check it never exercises.
- `eslint-plugin-jest`'s `valid-expect` flags async assertions that are not awaited or returned, and its
  `alwaysAwait` option insists on `await` over `return` inside block bodies.

## Better

```typescript
test("rejects an expired token", async () => {
  const token = makeToken({ expiresAt: yesterday() });

  await expect(verify(token)).rejects.toThrow(TokenExpiredError);
});
```
