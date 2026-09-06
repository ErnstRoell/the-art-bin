---
aliases: [if-elif-ladder, branch-chain-instead-of-dict]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: control-flow
tags: [dispatch, lookup-table, open-closed]
keywords: ["= None", "elif name ==", "elif fmt ==", "elif clf_name ==", "data = None", "else:"]
signature: "A chain of if/elif branches tests one variable for equality against constants and assigns to a single target, so the mapping cannot be read, extended, or iterated."
distinguish: "Fine when the conditions are not all equality tests on one variable, such as range checks, compound predicates, or tests whose order decides the answer."
added: 2026-09-05
source: ernst
---

# Equality chain instead of lookup table

## Smell

```python
FORMATS = ("csv", "json", "parquet")  # the closed set the caller picks from


def load_report(fmt, path):
    parsed = None
    if fmt == "csv":
        parsed = read_csv(path)
    elif fmt == "json":
        parsed = read_json(path)
    else:
        parsed = read_parquet(path)
    return parsed
```

## Why it's bad

- The code is a mapping from three names to three callables, written as control flow. Nothing can treat it as
  a mapping: it cannot be iterated to build a menu, checked against `FORMATS`, extended by a plugin, or
  reused by a second function that needs the same table.
- `"parquet"` never appears in the function. The third case exists only as "not csv and not json", so the
  one place that defines what the program supports and the one place that dispatches on it cannot be compared
  by eye, by `grep`, or by a test.
- The `parsed = None` preamble exists only because the branches assign instead of returning, which means
  every reader has to scan to the end to learn whether some path leaves it `None`.
- Adding a format means editing the chain *and* `FORMATS`, and forgetting the chain is silent — the new name
  falls into the `else` and is parsed as parquet.
- This is not the string-typing complaint. Replace `fmt` with an `enum.Enum` and every criticism above still
  holds, which is what separates it from `stringly-typed-mode-parameter`; that entry is about what is switched
  on, this one is about the shape of the branches. `isinstance-chain-instead-of-dispatch` is the same shape
  switching on type, where the fix is a method rather than a table.

## Better

```python
LOADERS = {
    "csv": read_csv,
    "json": read_json,
    "parquet": read_parquet,
}


def load_report(fmt, path):
    return LOADERS[fmt](path)
```

Now `tuple(LOADERS)` *is* the menu, so the supported set and the dispatch cannot drift apart, and an unknown
name raises `KeyError` at the lookup rather than being parsed as whichever format the `else` happened to hold.
