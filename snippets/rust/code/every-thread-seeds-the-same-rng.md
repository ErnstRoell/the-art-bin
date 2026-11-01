---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: correctness
topic: concurrency
tags: [randomness, rand, reproducibility, simulation]
keywords: ["seed_from_u64(", "StdRng::", "SmallRng::", "thread::spawn", "par_iter()", "SEED"]
signature: "Each worker thread builds its generator from the same constant seed, so every worker draws the identical random stream."
distinguish: "Fine when each worker's seed is derived from the base seed and its worker index, or when the workers are meant to replay the same stream."
added: 2026-09-23
source: jeremy-wayland
---

# Every thread seeds the same RNG

## Smell

```rust
const SEED: u64 = 42;

pub fn simulate(paths_per_worker: usize, workers: usize) -> Vec<f64> {
    let handles: Vec<_> = (0..workers)
        .map(|_| std::thread::spawn(move || {
            let mut rng = StdRng::seed_from_u64(SEED);
            (0..paths_per_worker).map(|_| one_path(&mut rng)).collect::<Vec<_>>()
        }))
        .collect();
    handles.into_iter().flat_map(|handle| handle.join().unwrap()).collect()
}
```

## Why it's bad

- Every worker produces the same sequence, so eight workers give eight copies of one sample. The estimate
  has the variance of one worker's worth of paths while claiming eight.
- Nothing errors and the numbers look plausible. The duplication shows only if someone checks for repeated
  values, which is how it presents: suspiciously tight confidence intervals.
- The seed was added for reproducibility, which is a good instinct; the mistake is using it verbatim instead of
  deriving one stream per worker.

## Better

```rust
const SEED: u64 = 42;

pub fn simulate(paths_per_worker: usize, workers: usize) -> Vec<f64> {
    let handles: Vec<_> = (0..workers as u64)
        .map(|worker| std::thread::spawn(move || {
            let mut rng = ChaCha8Rng::seed_from_u64(SEED);
            rng.set_stream(worker); // independent per worker, still reproducible
            (0..paths_per_worker).map(|_| one_path(&mut rng)).collect::<Vec<_>>()
        }))
        .collect();
    handles.into_iter().flat_map(|handle| handle.join().unwrap()).collect()
}
```
