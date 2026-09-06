---
aliases: []
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: []
keywords: []
signature: "One sentence naming the mechanism, written to be matched against unfamiliar code."
distinguish: "One sentence describing the near miss — code that looks like this but is fine."
added: 2026-01-01
source: your-handle
---

# Human readable name of the smell

## Smell

```python
# At most 15 lines in code/, 40 in architecture/. One smell. Must parse; need not run.
# Write this from scratch — never paste from a real codebase.
```

## Why it's bad

- The mechanism: what actually goes wrong, and when.
- How the failure presents itself, since that is what makes it recognisable in the wild.

## Better

```python
# What to write instead. Required, even when it seems obvious.
```
