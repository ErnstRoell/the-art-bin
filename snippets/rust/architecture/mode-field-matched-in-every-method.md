---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [strategy, traits, generics, enums]
keywords: ["mode: Mode", "match self.mode {", "Mode::Fast =>", "Mode::Accurate =>", "self.mode ==", "kind: Kind"]
signature: "One mode field is matched in every method of a struct, so a single algorithm is smeared across the impl instead of living in one type."
distinguish: "Fine when the enum is data the struct describes rather than a choice of algorithm, or when there is only one method that branches on it."
added: 2026-09-23
source: refactoring.guru
---

# Mode field matched in every method

## Smell

```rust
pub enum Mode { Lru, Fifo, Ttl(Duration) }

pub struct Cache<V> {
    mode: Mode,
    entries: HashMap<String, (V, Instant)>,
    order: VecDeque<String>,
}

impl<V> Cache<V> {
    pub fn get(&mut self, key: &str) -> Option<&V> {
        match self.mode {
            Mode::Lru => self.touch(key),
            Mode::Fifo => {}
            Mode::Ttl(ttl) => self.expire_older_than(ttl),
        }
        self.entries.get(key).map(|(value, _)| value)
    }

    pub fn insert(&mut self, key: String, value: V) {
        match self.mode {
            Mode::Lru | Mode::Fifo => self.evict_if_full(),
            Mode::Ttl(ttl) => self.expire_older_than(ttl),
        }
        self.order.push_back(key.clone());
        self.entries.insert(key, (value, Instant::now()));
    }

    fn evict_if_full(&mut self) {
        match self.mode {
            Mode::Lru => { /* evict least recently touched */ }
            Mode::Fifo => { /* evict oldest inserted */ }
            Mode::Ttl(_) => unreachable!(),
        }
    }
}
```

## Why it's bad

- The LRU policy is not anywhere; it is a fragment in each method. Understanding one policy means reading every
  method and mentally discarding the other arms.
- `unreachable!()` in `evict_if_full` is an invariant between methods that only holds as long as nobody edits
  `insert`, and a panic is what enforces it.
- `order` is needed by two modes and ignored by the third, so the struct carries the state of every policy at
  once.
- A new policy, such as LFU, is an edit to every method of a struct that already works.

## Better

```rust
pub trait Eviction<K> {
    fn on_get(&mut self, key: &K);
    fn on_insert(&mut self, key: &K);
    fn victim(&mut self) -> Option<K>;
}

pub struct Lru<K> { recency: VecDeque<K> }
pub struct Fifo<K> { arrival: VecDeque<K> }

pub struct Cache<K, V, E> {
    entries: HashMap<K, V>,
    policy: E,
    capacity: usize,
}

impl<K: Eq + Hash + Clone, V, E: Eviction<K>> Cache<K, V, E> {
    pub fn get(&mut self, key: &K) -> Option<&V> {
        self.policy.on_get(key);
        self.entries.get(key)
    }

    pub fn insert(&mut self, key: K, value: V) {
        if self.entries.len() >= self.capacity {
            if let Some(victim) = self.policy.victim() {
                self.entries.remove(&victim);
            }
        }
        self.policy.on_insert(&key);
        self.entries.insert(key, value);
    }
}
```

Each policy is one type with its own state, the cache is generic over it, and a new policy is a new type.
