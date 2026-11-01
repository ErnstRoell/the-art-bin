---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: io
tags: [logging, observability, node, javascript]
keywords: ["console.log(", "console.error(", "console.warn(", "console.info(", "console.debug("]
signature: "Service code reports what it is doing through console.log with concatenated strings, so there are no levels to filter by and no fields to query."
distinguish: "Fine in command-line tools whose output is meant for a person at a terminal, in one-off scripts, and in temporary debugging that is removed before merge."
added: 2026-09-30
source: Node.js Best Practices (goldbergyoni)
---

# console.log used as logging

## Smell

```typescript
export async function chargeCustomer(customerId: string, amountCents: number) {
  console.log("charging customer " + customerId + " amount " + amountCents);
  try {
    const charge = await payments.charge(customerId, amountCents);
    console.log("charge ok", charge.id);
    return charge;
  } catch (err) {
    console.log("charge failed", err);
    throw err;
  }
}
```

## Why it's bad

- The failure goes out through the same call as the success, so there is no level to alert on, and no way to
  turn chatty messages down in production without deleting them.
- The customer id is buried in free text, so a log search for one customer's charges is a regex over messages
  rather than a query on a field.
- The Node.js console is neither consistently synchronous nor consistently asynchronous; its behaviour depends
  on what stdout is attached to, which is not something to discover under load.

## Better

```typescript
import { logger } from "./logger"; // a pino instance, configured once per service

export async function chargeCustomer(customerId: string, amountCents: number) {
  const log = logger.child({ customerId, amountCents });
  log.info("charging customer");
  try {
    const charge = await payments.charge(customerId, amountCents);
    log.info({ chargeId: charge.id }, "charge succeeded");
    return charge;
  } catch (err) {
    log.error({ err }, "charge failed");
    throw err;
  }
}
```
