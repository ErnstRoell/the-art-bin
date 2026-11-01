---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: typing
tags: [dispatch, traits, any, polymorphism]
keywords: ["downcast_ref::<", "as_any()", "&dyn Any", "type_id()", "TypeId::of::<", "is::<"]
signature: "Code switches on a trait object's concrete type with a chain of downcasts, so adding a type means finding and editing every chain."
distinguish: "Fine at a genuine type-erasure boundary such as a plugin registry, an ECS or a boxed error, where the set of types is open and owned elsewhere."
added: 2026-09-23
source: jeremy-wayland
---

# Downcast chain instead of trait method

## Smell

```rust
pub fn area(shape: &dyn Shape) -> f64 {
    let any = shape.as_any();
    if let Some(c) = any.downcast_ref::<Circle>() {
        std::f64::consts::PI * c.radius * c.radius
    } else if let Some(r) = any.downcast_ref::<Rect>() {
        r.width * r.height
    } else {
        0.0
    }
}
```

## Why it's bad

- The crate owns `Shape` and every type behind it, so it already has two tools that make this checkable — a
  trait method and an enum — and uses neither.
- A new `Triangle` compiles and has an area of zero. The fallback that hides it is the only way this shape of
  code can end.
- The `as_any` plumbing on the trait exists only to support this, and every implementor has to carry it.

## Better

```rust
pub trait Shape {
    fn area(&self) -> f64;
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }
}

impl Shape for Rect {
    fn area(&self) -> f64 {
        self.width * self.height
    }
}
```

A new type that forgets `area` is now a compile error. If the set of shapes is closed and the operations keep
growing, an enum with one `match` per operation is the better shape; see
`operation-added-to-every-impl-of-a-trait`.
