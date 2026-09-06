---
aliases: [clipped-names, vowel-free-naming]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: naming
tags: [naming, abbreviations, house-style]
keywords: ["cfg", "res =", "tmp", "val =", "idx", "num_", "ret ="]
signature: "Identifiers are clipped to abbreviations such as cfg, res, or val, so the reader has to decode them."
distinguish: "Fine for abbreviations that are standard in the domain, such as df for a dataframe or url for a locator."
added: 2026-09-04
source: ernst
---

# Abbreviated identifier

## Smell

```python
def calc(df, cfg):
    res = []
    for idx, r in df.iterrows():
        v = r["val"] * cfg["mult"]
        res.append(v)
    return res
```

## Why it's bad

- Nothing here says what is being computed. `calc`, `res`, and `v` describe the *shape* of the operation, which
  the code already shows, and omit the subject, which the code cannot.
- Abbreviation is lossy in one direction only: expanding `cfg` to `config` costs three characters, while
  recovering "multiplier" from `mult` requires reading the caller.
- The savings are illusory because the names appear a handful of times and are read hundreds, and because no
  modern editor requires anyone to type them in full.
- It presents as review comments asking what the function returns, and as a second implementation of the same
  logic elsewhere because nobody recognised `calc` as the thing they needed.

## Better

```python
def scaled_scores(measurements, config):
    scores = []
    for _, measurement in measurements.iterrows():
        scores.append(measurement["value"] * config["multiplier"])
    return scores
```
