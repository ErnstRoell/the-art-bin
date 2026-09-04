---
aliases: [java-style-accessors, getter-setter-pair]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: classes
tags: [api-design, properties, ceremony]
keywords: ["def get_", "def set_", "self._name", "return self._", "def get_name"]
signature: "A class exposes get and set methods that do nothing but read and write one plain attribute."
distinguish: "Fine when the accessor validates, converts, or computes, in which case it belongs as a property rather than a get method."
added: 2026-09-04
source: ernst
---

# Getter and setter wrapping a plain attribute

## Smell

```python
class Run:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
```

## Why it's bad

- The pair provides no encapsulation. Anything a caller could do with `run.name` it can do with the two
  methods, so the underscore is decoration and the class has a public mutable attribute either way.
- The usual justification is future-proofing — being able to add validation later without breaking callers —
  and in Python that is what `property` is for, so the future change is free without the ceremony now.
- Nine lines carry the information of one, and every additional field triples in the same way, which is how a
  data holder ends up two hundred lines long.
- Call sites read worse: `run.set_name(run.get_name().strip())` instead of `run.name = run.name.strip()`.

## Better

```python
import dataclasses


@dataclasses.dataclass
class Run:
    name: str
```
