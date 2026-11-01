---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: performance
topic: mutability
tags: [ownership, borrowing, allocation]
keywords: [".clone()", ".to_owned()", ".to_vec()", "let owned =", ".clone().iter()", ".clone().len()"]
signature: "A value is cloned where a borrow would do, usually to make a borrow-checker error go away, so the code pays for an allocation it never needed."
distinguish: "Fine when the clone is genuinely needed to hand ownership to another thread, task or long-lived struct, or when the type is a cheap handle such as Arc or Rc."
added: 2026-09-23
source: jeremy-wayland
---

# Clone to silence the borrow checker

## Smell

```rust
pub fn longest_name(users: &Vec<User>) -> String {
    let mut best = String::new();
    for user in users.clone() {
        if user.name.clone().len() > best.len() {
            best = user.name.clone();
        }
    }
    best
}
```

## Why it's bad

- `users.clone()` deep-copies every `User` and every `String` inside them just to iterate, and the loop clones
  each name again to ask its length.
- Clones added to silence an error tend to survive the refactor that made them unnecessary, so they read as
  "this needs ownership" when nothing does. The next reader cannot tell which clones are load-bearing.
- On a hot path the cost is real: allocator churn scales with the size of the data, not the size of the
  answer.

## Better

```rust
pub fn longest_name(users: &[User]) -> Option<&str> {
    users.iter().map(|user| user.name.as_str()).max_by_key(|name| name.len())
}
```
