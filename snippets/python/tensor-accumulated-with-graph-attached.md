---
aliases: [loss-accumulated-without-detach, retained-graph-leak]
language: python
python: ">=3.0"
severity: trap
category: performance
topic: numerics
tags: [pytorch, autograd, memory, training-loop]
keywords: ["total += loss", "losses.append(loss", ".detach()", ".item()", "loss.backward()"]
signature: "A tensor that requires grad is added into a running total or list without detach, so every step's computation graph stays reachable."
distinguish: "Fine when the accumulated tensor is genuinely part of the loss being differentiated, as when summing terms before a single backward call."
added: 2026-09-04
source: ernst
---

# Tensor accumulated with its graph attached

## Smell

```python
def train_epoch(model, loader, opt):
    total = 0.0
    for batch in loader:
        loss = model.loss(batch)
        loss.backward()
        opt.step()
        opt.zero_grad()
        total += loss
    return total / len(loader)
```

## Why it's bad

- `total += loss` builds a new tensor whose graph references `loss`, which references the activations of that
  step — so nothing from any step can be freed while `total` is alive.
- Memory therefore grows linearly across the epoch and the run dies partway through with a CUDA
  out-of-memory error whose size depends on the dataset, not on the model.
- The reported number is also a tensor rather than a float, so it silently carries `grad_fn` into whatever
  logs or stores it, propagating the leak.
- It presents as a job that trains fine for two hundred steps and then OOMs, which is usually blamed on batch
  size — and raising the batch size makes it fail sooner, confirming the wrong diagnosis.

## Better

```python
def train_epoch(model, loader, opt):
    total = 0.0
    for batch in loader:
        loss = model.loss(batch)
        loss.backward()
        opt.step()
        opt.zero_grad()
        total += loss.item()
    return total / len(loader)
```
