---
aliases: [unsafe-deserialisation, pickle-rce]
language: python
python: ">=3.0"
severity: bug
category: security
topic: io
tags: [deserialisation, checkpoints, remote-code-execution]
keywords: ["pickle.load", "pickle.loads", "torch.load", "joblib.load", "allow_pickle=True", "weights_only"]
signature: "A pickle stream is deserialised from a file the program did not produce, so loading it executes arbitrary code."
distinguish: "Fine when the data never leaves one trust boundary, or when the format cannot execute code, as with JSON or safetensors."
added: 2026-09-04
source: ernst
---

# Pickle loaded from an untrusted file

## Smell

```python
def load_checkpoint(url):
    blob = requests.get(url).content
    return pickle.loads(blob)


weights = torch.load("downloaded.ckpt")
```

## Why it's bad

- Unpickling is not parsing. The format is a small stack language with an opcode for calling arbitrary
  importable objects, so a crafted file runs code the moment it is read — before any of your validation.
- `torch.load` and `joblib.load` are pickle underneath, as is `numpy.load` with `allow_pickle=True`, so a model
  checkpoint from a hub or a colleague's bucket is executable content that looks like data.
- There is nothing to check afterwards: the payload runs during load, so inspecting the returned object tells
  you only what the attacker chose to return.
- It presents as no failure at all, which is the point — a compromised checkpoint trains normally and
  exfiltrates whatever the process can reach.

## Better

```python
import safetensors.torch


def load_checkpoint(path):
    return safetensors.torch.load_file(path)


weights = torch.load("downloaded.ckpt", weights_only=True)
```
