---
aliases: [missing-encoding-argument, platform-default-encoding]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: io
tags: [encoding, files, portability]
keywords: ["open(", "open(path)", '"r")', ".read_text()", "encoding="]
signature: "A text file is opened without an explicit encoding, so the platform default decides how its bytes are decoded."
distinguish: "Fine for binary modes such as rb and wb, which do not accept an encoding argument and do no decoding."
added: 2026-09-04
source: ernst
---

# Text file opened without an encoding

## Smell

```python
def read_config(path):
    with open(path) as handle:
        return json.load(handle)
```

## Why it's bad

- Without `encoding=`, Python uses `locale.getpreferredencoding()`, which is UTF-8 on most Linux machines and
  historically cp1252 on Windows, so the same file parses differently on two developers' laptops.
- The failure is content-dependent: files of pure ASCII behave identically everywhere, so the bug appears only
  once a name contains an accent or a dash that is not the ASCII hyphen.
- When decoding does fail it raises `UnicodeDecodeError` pointing at a byte offset, which reads as a corrupt
  file rather than a wrong assumption about the reader.
- Worse than the crash is the silent case, where cp1252 decodes UTF-8 bytes into mojibake without error and the
  wrong string is stored.

## Better

```python
def read_config(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
```
