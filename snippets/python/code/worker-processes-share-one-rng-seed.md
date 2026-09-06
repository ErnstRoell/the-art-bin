---
aliases: [duplicate-augmentations, forked-rng-state]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: concurrency
tags: [dataloader, randomness, forking, augmentation]
keywords: ["num_workers", "np.random.", "DataLoader", "__getitem__", "worker_init_fn"]
signature: "A dataset draws from the global numpy generator while loader workers are forked, so every worker replays the same random stream."
distinguish: "Fine when the randomness comes from torch's own generator, which the loader reseeds per worker, or when a worker_init_fn seeds each one."
added: 2026-09-04
source: ernst
---

# Worker processes share one RNG seed

## Smell

```python
class Augmented(Dataset):
    def __getitem__(self, index):
        angle = np.random.uniform(-10, 10)
        return rotate(self.images[index], angle)


loader = DataLoader(Augmented(), num_workers=4)
```

## Why it's bad

- Each worker is a fork of the parent, so all four inherit an identical copy of numpy's global generator state
  and then advance it independently and identically.
- Every worker therefore produces the same sequence of angles, so the batch that should contain four
  independent augmentations contains the same four, epoch after epoch.
- PyTorch reseeds its *own* generator per worker, so `torch.rand` in the same method would be correct — which
  is why the bug survives review by anyone who knows the loader reseeds.
- It presents as augmentation that stops helping: the effective diversity of the data is a quarter of what the
  code says, and the only symptom is a validation curve that plateaus early.

## Better

```python
class Augmented(Dataset):
    def __getitem__(self, index):
        angle = torch.empty(1).uniform_(-10, 10).item()
        return rotate(self.images[index], angle)


loader = DataLoader(Augmented(), num_workers=4)
```
