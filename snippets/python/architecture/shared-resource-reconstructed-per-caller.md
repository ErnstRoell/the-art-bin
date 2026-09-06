---
aliases: [missing-singleton, instance-per-call-site]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [singleton, shared-state, caching, composition-root]
keywords: ["= Client()", "= Flags()", "Settings()", "def __init__(self)", "requests.get", "load_config()"]
signature: "A class holding shared state or an expensive resource is instantiated afresh by each caller, so the copies disagree with each other and the cost is paid once per call site."
distinguish: "Fine when the class is a cheap value object whose instances hold nothing that needs to be shared."
added: 2026-09-06
source: refactoring.guru
---

# Shared resource reconstructed per caller

## Smell

```python
class FeatureFlags:
    def __init__(self):
        self._flags = fetch_flags()          # one network round trip, per instance
        self._overrides = {}

    def enabled(self, name):
        return self._overrides.get(name, self._flags.get(name, False))

    def override(self, name, value):
        self._overrides[name] = value


def checkout(cart):
    if FeatureFlags().enabled("new_pricing"):    # fetches again, sees no overrides
        return new_price(cart)
    return old_price(cart)


def banner(user):
    flags = FeatureFlags()                       # a third copy, a third fetch
    return "new" if flags.enabled("new_pricing") else "old"
```

## Why it's bad

- The class is written as if there were one of it — it holds overrides, and overrides only mean anything if
  everyone reads the same instance. There are three, so `override` affects nobody and a test that sets one
  watches the code under test ignore it.
- The copies can disagree. Two `FeatureFlags()` built either side of a flag flip give two answers in the same
  request, and the resulting bug report describes a page that was half new and half old.
- The fetch in `__init__` means the cost scales with call sites rather than with processes, which is
  `constructor-does-io` seen from outside: the caller cannot tell that naming a class made an HTTP request.
- The fix is *one instance*, which is not the same as a global. A class that reaches for itself through a
  module-level `_instance` is `global-statement-for-shared-state` wearing a constructor, and it takes the
  testability problem with it.

## Better

```python
class FeatureFlags:
    def __init__(self, flags):
        self._flags = flags
        self._overrides = {}

    def enabled(self, name):
        return self._overrides.get(name, self._flags.get(name, False))

    def override(self, name, value):
        self._overrides[name] = value


def checkout(cart, flags):
    return new_price(cart) if flags.enabled("new_pricing") else old_price(cart)


def banner(user, flags):
    return "new" if flags.enabled("new_pricing") else "old"


# One instance, built once, where the process starts:
#     flags = FeatureFlags(fetch_flags())
```

Sharing is now visible in the signatures: a function that reads flags says so, a test passes
`FeatureFlags({"new_pricing": True})`, and the fetch happens once because there is one place that does it.
