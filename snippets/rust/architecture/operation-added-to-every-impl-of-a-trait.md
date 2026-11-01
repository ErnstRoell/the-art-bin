---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [visitor, expression-problem, enums, traits]
keywords: ["fn to_svg(&self)", "fn to_dxf(&self)", "fn price(&self", "impl Shape for", "trait Shape {", "fn validate(&self"]
signature: "Each new operation over a closed set of types is added as a trait method implemented on every one of them, so one concern is spread across all the impls and each type collects unrelated reasons to change."
distinguish: "Fine when the set of types is open and other crates add implementations, since a trait is the only way to let them, or when the operation is the type's own behaviour rather than an outside concern."
added: 2026-09-23
source: refactoring.guru
---

# Operation added to every impl of a trait

## Smell

```rust
pub trait Shape {
    fn area(&self) -> f64;
    fn to_svg(&self) -> String;
    fn to_dxf(&self) -> String;
    fn price(&self, rates: &Rates) -> Money;
}

impl Shape for Circle {
    fn area(&self) -> f64 { PI * self.radius * self.radius }
    fn to_svg(&self) -> String { format!(r#"<circle r="{}"/>"#, self.radius) }
    fn to_dxf(&self) -> String { format!("CIRCLE {}", self.radius) }
    fn price(&self, rates: &Rates) -> Money { rates.circle * self.area() }
}

impl Shape for Square {
    fn area(&self) -> f64 { self.side * self.side }
    fn to_svg(&self) -> String { format!(r#"<rect width="{0}" height="{0}"/>"#, self.side) }
    fn to_dxf(&self) -> String { format!("POLYLINE {}", self.side) }
    fn price(&self, rates: &Rates) -> Money { rates.square * self.area() }
}

// the next request is validation, then JSON export, then collision checks
```

## Why it's bad

- The set of shapes is settled; the set of operations is not. Every new thing anyone wants to do with a shape
  widens the trait and edits every impl, in files owned by the geometry code.
- One concern is split across N impls, so reviewing "how do we export DXF" means reading every shape and
  hoping to find them all.
- The shape module now depends on pricing rates and export formats, so geometry cannot be used without them.
- A trait is the right tool when the types are open, because other crates can implement it. When the crate
  owns every shape, it is paying for openness it does not use.

## Better

```rust
pub enum Shape {
    Circle { radius: f64 },
    Square { side: f64 },
}

impl Shape {
    pub fn area(&self) -> f64 {
        match self {
            Shape::Circle { radius } => PI * radius * radius,
            Shape::Square { side } => side * side,
        }
    }
}

// svg.rs: one operation, complete for every shape, in one place.
pub fn to_svg(shape: &Shape) -> String {
    match shape {
        Shape::Circle { radius } => format!(r#"<circle r="{radius}"/>"#),
        Shape::Square { side } => format!(r#"<rect width="{side}" height="{side}"/>"#),
    }
}

// pricing.rs
pub fn price(shape: &Shape, rates: &Rates) -> Money {
    match shape {
        Shape::Circle { .. } => rates.circle * shape.area(),
        Shape::Square { .. } => rates.square * shape.area(),
    }
}
```

In Rust, a closed enum with a `match` per operation is the visitor pattern with the compiler as its enforcer:
a new operation is one new function, and a new shape is an exhaustiveness error in each of them.
