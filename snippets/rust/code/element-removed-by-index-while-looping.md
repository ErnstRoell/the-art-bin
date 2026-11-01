---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: correctness
topic: control-flow
tags: [vec, collections, iteration, borrow-checker]
keywords: [".remove(i)", "while i < ", "for i in 0..", "i += 1", ".swap_remove(i)"]
signature: "Elements are removed from a Vec by index inside a loop that advances the index regardless, so the element that slides into the removed slot is skipped."
distinguish: "Fine when a single element is removed at a position found beforehand, such as the result of position, and the loop ends there."
added: 2026-09-23
source: jeremy-wayland
---

# Element removed by index while looping

## Smell

```rust
pub fn drop_expired(sessions: &mut Vec<Session>, now: Instant) {
    let mut i = 0;
    while i < sessions.len() {
        if sessions[i].expires_at <= now {
            sessions.remove(i);
        }
        i += 1;
    }
}
```

## Why it's bad

- The borrow checker forbids removing from a `Vec` while a `for` loop borrows it, so the index loop is how
  the Python bug is reintroduced. After `remove(i)` the next element moves into slot `i`, and `i += 1` steps
  over it.
- Two adjacent expired sessions leave one behind. It presents as an occasional survivor that the next sweep
  cleans up, which looks like a timing issue.
- Even the correct variant, iterating in reverse, is quadratic, because every `remove` shifts the tail.

## Better

```rust
pub fn drop_expired(sessions: &mut Vec<Session>, now: Instant) {
    sessions.retain(|session| session.expires_at > now);
}
```

When the removed elements are needed too, `Vec::extract_if` (Rust 1.87) returns them in the same single pass.
