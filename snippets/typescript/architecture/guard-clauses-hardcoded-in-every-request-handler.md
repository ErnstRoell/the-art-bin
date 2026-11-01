---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: control-flow
tags: [chain-of-responsibility, middleware, policy, composition]
keywords: ["return deny(", "if (!token)", "if (rateLimited(", "if (maintenanceMode())", "headers.get(\"authorization\")", "export async function handle"]
signature: "Independent policy checks are hardcoded as a fixed sequence of early returns in each handler, so no entry point can add, remove or reorder them without copying the pile."
distinguish: "Fine when the checks are not independent policies but the logic of that one handler, where reordering them would be a bug rather than a configuration."
added: 2026-09-30
source: refactoring.guru
---

# Guard clauses hardcoded in every request handler

## Smell

```typescript
export async function handleApi(req: Request): Promise<Response> {
  const token = req.headers.get("authorization");
  if (!token) return deny(401, "no token");
  if (!(await validToken(token))) return deny(401, "bad token");
  if (rateLimited(clientIp(req))) return deny(429, "slow down");
  if (maintenanceMode()) return deny(503, "try later");
  if (Number(req.headers.get("content-length")) > 1_000_000) return deny(413, "too large");
  return route(req);
}

export async function handleWebhook(req: Request): Promise<Response> {
  if (!(await validSignature(req))) return deny(401, "bad signature");
  if (rateLimited(clientIp(req))) return deny(429, "slow down");   // the same pile again,
  if (maintenanceMode()) return deny(503, "try later");            // minus auth, plus signatures
  return route(req);
}
```

## Why it's bad

- Five independent policies live inside one function, and the only way to have three of them is to write the
  function again. `handleWebhook` is that copy, and the two now share rate limiting by duplication.
- The order is policy: authenticating before rate limiting means an unauthenticated flood still hits the token
  service. Here the order is line numbers, so it cannot be reviewed as a decision or varied per route.
- No check can be tested alone. Reaching the size limit requires a request with a valid token that is not rate
  limited in a system not under maintenance.
- Adding a policy edits every handler that should have it, and forgetting one is silent.

## Better

```typescript
/** A step answers, or returns undefined to pass the request along the chain. */
type Check = (req: Request) => Promise<Response | undefined> | Response | undefined;

const chain = (...checks: Check[]) => async (req: Request): Promise<Response> => {
  for (const check of checks) {
    const answer = await check(req);
    if (answer) return answer;
  }
  return route(req);
};

const rateLimit: Check = (req) => (rateLimited(clientIp(req)) ? deny(429, "slow down") : undefined);
const notInMaintenance: Check = () => (maintenanceMode() ? deny(503, "try later") : undefined);
const requireToken: Check = async (req) => {
  const token = req.headers.get("authorization");
  return token && (await validToken(token)) ? undefined : deny(401, "bad token");
};
const requireSignature: Check = async (req) =>
  (await validSignature(req)) ? undefined : deny(401, "bad signature");

// Each entry point states its chain, in order, as one line:
export const handleApi = chain(rateLimit, notInMaintenance, requireToken);
export const handleWebhook = chain(rateLimit, notInMaintenance, requireSignature);
```

Each policy is a function tested with a chain of one, and the order is a line a reviewer can point at. When the
service already runs on Express, Koa or Hono, their middleware stack is this chain and is the one to use.
