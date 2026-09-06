---
aliases: [cuda-hardcoded, cuda-call-not-parameterised]
language: python
python: ">=3.0"
severity: trap
category: maintainability
topic: numerics
tags: [pytorch, devices, portability]
keywords: [".cuda()", 'device="cuda"', "cuda:0", "torch.device", ".to(device)"]
signature: "Code names cuda directly instead of taking a device, so it cannot run on cpu or on a chosen gpu."
distinguish: "Fine in a script whose only job is one gpu run, or in a benchmark deliberately pinned to a device."
added: 2026-09-04
source: ernst
---

# Hardcoded cuda device

## Smell

```python
def embed(model, batch):
    model = model.cuda()
    batch = batch.to("cuda")
    return model(batch)
```

## Why it's bad

- The function will not run on a machine without a GPU, so nobody can execute the test suite on a laptop and
  CI has to be given hardware it does not need.
- `"cuda"` means device zero, so on a multi-GPU host every call lands on the same card no matter what the
  caller arranged, and two parallel jobs fight over it.
- The device is a property of the run, not of this function, so hardcoding it removes the one decision the
  caller actually needs to make while leaving the function no less complicated.
- It presents as a `RuntimeError` about tensors on different devices, raised somewhere downstream, once one
  more function in the chain is written slightly differently.

## Better

```python
def embed(model, batch, device):
    model = model.to(device)
    return model(batch.to(device))
```
