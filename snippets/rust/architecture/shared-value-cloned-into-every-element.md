---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: performance
topic: classes
tags: [flyweight, arc, interning, memory]
keywords: ["style: Style", "font: Font", "style.clone()", "texture: Vec<u8>", "Arc<", "for _ in 0.."]
signature: "Every element in a large collection owns its own clone of state that is identical across them, so memory and setup cost scale with the number of elements rather than the number of distinct values."
distinguish: "Fine when the shared part is small and Copy, or when each element is expected to modify its copy independently."
added: 2026-09-23
source: refactoring.guru
---

# Shared value cloned into every element

## Smell

```rust
#[derive(Clone)]
pub struct TreeKind {
    pub name: String,
    pub texture: Vec<u8>,       // 2 MB of pixels
    pub bark_color: Rgb,
}

pub struct Tree {
    pub x: f32,
    pub y: f32,
    pub kind: TreeKind,
}

pub fn plant_forest(kinds: &[TreeKind], count: usize, rng: &mut impl Rng) -> Vec<Tree> {
    (0..count)
        .map(|_| Tree {
            x: rng.gen(),
            y: rng.gen(),
            kind: kinds.choose(rng).unwrap().clone(),   // copies the texture
        })
        .collect()
}
```

## Why it's bad

- A million trees of three kinds hold a million copies of the same three textures: two terabytes of identical
  bytes, where six megabytes carry the information.
- Each clone is an allocation and a memcpy, so planting the forest is dominated by copying textures rather than
  by anything the game does.
- The copies are independent, so changing a kind's bark colour means walking every tree, and missing one
  leaves a visibly different tree.

## Better

```rust
pub struct TreeKind {
    pub name: String,
    pub texture: Vec<u8>,
    pub bark_color: Rgb,
}

pub struct Tree {
    pub x: f32,
    pub y: f32,
    pub kind: Arc<TreeKind>,    // shared, cloned as a pointer
}

pub fn plant_forest(kinds: &[Arc<TreeKind>], count: usize, rng: &mut impl Rng) -> Vec<Tree> {
    (0..count)
        .map(|_| Tree { x: rng.gen(), y: rng.gen(), kind: Arc::clone(kinds.choose(rng).unwrap()) })
        .collect()
}
```

Each tree keeps only what is its own, its position, and points at the shared kind. An index into a `Vec` of
kinds works as well when trees never outlive the table.
