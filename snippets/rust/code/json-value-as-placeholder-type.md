---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: typing
tags: [serde, types, dynamic-data]
keywords: ["serde_json::Value", "-> Value", "value[\"", ".as_str().unwrap()", "HashMap<String, Value>", "Box<dyn Any>"]
signature: "Data whose shape is known is passed around as serde_json Value or a map of strings, so every field access is a runtime lookup the compiler cannot check."
distinguish: "Fine at the edge where the shape genuinely varies, such as proxying or storing arbitrary user JSON, as long as it is parsed into a type before any logic reads it."
added: 2026-09-23
source: jeremy-wayland
---

# JSON Value as placeholder type

## Smell

```rust
pub fn shipping_cost(order: &serde_json::Value) -> f64 {
    let weight = order["weight_kg"].as_f64().unwrap_or(0.0);
    let country = order["address"]["country"].as_str().unwrap_or("");
    let express = order["express"].as_bool().unwrap_or(false);
    rate_for(country, express) * weight
}
```

## Why it's bad

- A misspelt key such as `weight_kgs` is not an error; it is `Null`, which becomes `0.0`, which ships the
  order for free.
- The expected shape of an order exists only in the string literals scattered through the functions that read
  it, so nothing documents it and nothing checks it.
- Validation is repeated per field and per function, each with its own default, instead of once where the JSON
  enters the program.

## Better

```rust
#[derive(serde::Deserialize)]
pub struct Order {
    pub weight_kg: f64,
    pub address: Address,
    #[serde(default)]
    pub express: bool,
}

pub fn shipping_cost(order: &Order) -> f64 {
    rate_for(&order.address.country, order.express) * order.weight_kg
}
```
