---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: mutability
tags: [aliasing, rc, refcell, shared-ownership]
keywords: ["Rc<RefCell<", "Arc<Mutex<", "#[derive(Clone)]", ".clone()", "borrow_mut()"]
signature: "A struct holding Rc or Arc handles to mutable data is cloned as if that produced an independent copy, so writes through the copy reach the original."
distinguish: "Fine when sharing is the point, such as handing several owners the same cache or connection, and the struct's name or docs say so."
added: 2026-09-23
source: jeremy-wayland
---

# Rc clone mistaken for deep copy

## Smell

```rust
#[derive(Clone)]
pub struct Scenario {
    pub name: String,
    pub prices: Rc<RefCell<Vec<f64>>>,
}

pub fn stressed(base: &Scenario) -> Scenario {
    let mut scenario = base.clone();
    scenario.name = format!("{} (stressed)", base.name);
    scenario.prices.borrow_mut().iter_mut().for_each(|p| *p *= 0.8);
    scenario
}
```

## Why it's bad

- `#[derive(Clone)]` clones each field, and cloning an `Rc` clones the pointer. The new scenario and the base
  scenario hold the same `Vec`, so stressing one stresses both.
- `name` really is copied, which makes the struct look like a value type and the shared field easy to miss.
- It presents as the baseline report quietly showing stressed numbers, with no borrow error or panic anywhere,
  because `RefCell` permits the write.

## Better

```rust
#[derive(Clone)]
pub struct Scenario {
    pub name: String,
    pub prices: Vec<f64>,
}

pub fn stressed(base: &Scenario) -> Scenario {
    Scenario {
        name: format!("{} (stressed)", base.name),
        prices: base.prices.iter().map(|p| p * 0.8).collect(),
    }
}
```
