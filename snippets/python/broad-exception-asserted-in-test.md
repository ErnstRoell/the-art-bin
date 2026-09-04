---
aliases: [pytest-raises-exception, assert-raises-broad]
language: python
python: ">=3.0"
severity: trap
category: testability
topic: stdlib-misuse
tags: [tests, assertions, false-confidence]
keywords: ["pytest.raises(Exception)", "assertRaises(Exception)", "with pytest.raises", "match="]
signature: "A test asserts that Exception is raised, so any failure inside the block satisfies it including a mistake in the test."
distinguish: "Fine when the assertion names the specific type and pins the message with match or assertRaisesRegex."
added: 2026-09-04
source: ernst
---

# Broad exception asserted in a test

## Smell

```python
def test_rejects_bad_port():
    with pytest.raises(Exception):
        parse_confg("port: bananas")
```

## Why it's bad

- The typo in `parse_confg` raises `NameError`, which is an `Exception`, so the test passes without ever
  calling the function it claims to test.
- Even spelled correctly the assertion is nearly vacuous: an `ImportError`, an `AttributeError` from a renamed
  method, or a `TypeError` from a changed signature all satisfy it.
- That makes the test worse than absent, because it is green, so the coverage report counts this line and
  nobody revisits it.
- It presents as a suite that stays green through a refactor that broke the behaviour under test — the failure
  moved from the assertion into the setup, where the assertion cannot see it.

## Better

```python
def test_rejects_bad_port():
    with pytest.raises(ConfigError, match="port must be a number"):
        parse_config("port: bananas")
```
