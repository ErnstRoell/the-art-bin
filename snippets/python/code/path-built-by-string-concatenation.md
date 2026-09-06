---
aliases: [manual-path-joining, string-concatenated-path]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: io
tags: [paths, pathlib, portability]
keywords: ['+ "/"', 'run_dir +', 'os.path.join', '+ ".pt"', 'f"{root}/{name}"']
signature: "A filesystem path is assembled by concatenating strings with separators written by hand."
distinguish: "Fine for a URL or an object-store key, which is not a filesystem path and always uses a forward slash."
added: 2026-09-04
source: ernst
---

# Path built by string concatenation

## Smell

```python
def checkpoint_path(run_dir, epoch):
    return run_dir + "/ckpt_" + str(epoch) + ".pt"
```

## Why it's bad

- The separator is now the caller's problem: a `run_dir` that already ends in `/` produces a doubled slash, and
  one that is empty produces an absolute path pointing at the filesystem root.
- Nothing normalises the result, so the same location can be spelled several ways and dictionary keys, caches,
  and equality checks over these strings quietly disagree.
- The `str(epoch)` conversion is load-bearing and easy to omit, giving a `TypeError` that names string
  concatenation rather than the missing conversion.
- It presents as a file written to an unexpected location — often the current directory or `/` — which looks
  like a configuration error until someone prints the assembled path.

## Better

```python
import pathlib


def checkpoint_path(run_dir, epoch):
    return pathlib.Path(run_dir) / f"ckpt_{epoch}.pt"
```
