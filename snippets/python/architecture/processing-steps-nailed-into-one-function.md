---
aliases: [missing-chain-of-responsibility, fixed-pile-of-guard-clauses]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: control-flow
tags: [chain-of-responsibility, middleware, policy, composition]
keywords: ["def handle(", "return deny(", "if not request.", "rate_limited(", "return None", "early return"]
signature: "Independent policy steps are hardcoded as a fixed sequence of early returns in one function, so no caller can add, remove or reorder them."
distinguish: "Fine when the steps are not independent policies but the logic of that one function, where reordering them would be a bug rather than a configuration."
added: 2026-09-06
source: refactoring.guru
---

# Processing steps nailed into one function

## Smell

```python
def handle(request):
    if not request.token:
        return deny("no token")
    if not valid_token(request.token):
        return deny("bad token")
    if rate_limited(request.ip):
        return deny("slow down")
    if maintenance_mode():
        return deny("try later")
    if request.body and not schema_ok(request.body):
        return deny("bad body")
    if request.path in CACHE:
        return CACHE[request.path]
    return route(request)


def handle_webhook(request):
    if not valid_signature(request):        # the same pile, minus auth, plus signatures
        return deny("bad signature")
    if rate_limited(request.ip):
        return deny("slow down")
    if maintenance_mode():
        return deny("try later")
    return route(request)
```

## Why it's bad

- Six independent policies live in one function, and the only way to have five of them is to write the function
  again. `handle_webhook` is that second copy, and the two now share rate limiting and maintenance mode by
  duplication.
- The order is policy — rate limiting before authentication means unauthenticated traffic can exhaust a
  budget — but the order is expressed as line numbers, so it cannot be reviewed as a decision, tested, or
  varied per route.
- Nothing can be tested alone. Reaching the schema check requires a request with a valid token that is not rate
  limited and a system not in maintenance, so every test of the last step reconstructs all the earlier ones.
- Adding a policy edits a function every endpoint depends on, which makes each addition a change with global
  blast radius and no way to enable it for one route first.

## Better

```python
class Step:
    """Each step decides, or passes the request along."""

    def __init__(self, nxt=None):
        self._next = nxt

    def handle(self, request):
        return self._next.handle(request) if self._next else route(request)


class RequireToken(Step):
    def handle(self, request):
        if not request.token or not valid_token(request.token):
            return deny("bad token")
        return super().handle(request)


class RateLimit(Step):
    def handle(self, request):
        if rate_limited(request.ip):
            return deny("slow down")
        return super().handle(request)


class RequireSignature(Step):
    def handle(self, request):
        if not valid_signature(request):
            return deny("bad signature")
        return super().handle(request)


# The chain is data, so each entry point composes the policies it wants:
api = RequireToken(RateLimit())
webhooks = RequireSignature(RateLimit())
```

The shared steps exist once, the order is a line you can point at in review, and `RateLimit` can be tested with
a chain of one.
