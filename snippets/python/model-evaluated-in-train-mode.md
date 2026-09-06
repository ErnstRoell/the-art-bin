---
aliases: [missing-model-eval, eval-without-no-grad]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: numerics
tags: [pytorch, dropout, batchnorm, evaluation]
keywords: ["model.eval()", "model.train()", "torch.no_grad", "with torch.inference_mode", "def accuracy"]
signature: "A model is run for evaluation without eval mode or no_grad, so dropout stays active and batch statistics keep updating."
distinguish: "Fine when the forward pass is part of training, or when the metric is deliberately computed on the model in training mode."
added: 2026-09-04
source: ernst
---

# Model evaluated in training mode

## Smell

```python
def accuracy(model, loader):
    correct = 0
    for images, labels in loader:
        logits = model(images)
        correct += (logits.argmax(-1) == labels).sum()
    return correct / len(loader.dataset)
```

## Why it's bad

- Dropout is still on, so predictions are made with a randomly crippled network and the score is both lower
  than the truth and different on every call.
- Batch norm layers are still in training mode, so this pass *updates the running statistics* using the
  validation set — the evaluation has now modified the model and leaked the held-out distribution into it.
- Without `no_grad` every forward also builds a graph that is never used, roughly doubling memory for no
  purpose, which is often what forces the batch size down.
- It presents as a validation number that is noisy and pessimistic, and as a model that scores differently
  after evaluation than before it, which reads as nondeterminism rather than as a missing method call.

## Better

```python
@torch.no_grad()
def accuracy(model, loader):
    model.eval()
    correct = 0
    for images, labels in loader:
        correct += (model(images).argmax(-1) == labels).sum()
    return correct / len(loader.dataset)
```
