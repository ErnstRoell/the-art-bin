---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: maintainability
topic: classes
tags: [adapter, from, conversions, anti-corruption-layer]
keywords: ["stripe::Customer", "api_user.", ".unwrap_or_default()", "impl From<", "as_deref().unwrap_or(", "metadata.get(\""]
signature: "A foreign API's types are translated into local terms inline wherever they are used, so the translation exists once per call site instead of once per API."
distinguish: "Fine when the foreign type is used in exactly one place, or when it is already the program's own domain type and no translation is needed."
added: 2026-09-23
source: refactoring.guru
---

# Foreign type converted inline at each use

## Smell

```rust
pub fn welcome_email(customer: &stripe::Customer) -> Email {
    let name = customer.name.as_deref().unwrap_or("there");
    let plan = customer.metadata.get("plan").map(String::as_str).unwrap_or("free");
    Email::new(customer.email.clone().unwrap_or_default(), format!("Hi {name}, welcome to {plan}"))
}

pub fn invoice_header(customer: &stripe::Customer) -> Header {
    Header {
        name: customer.name.clone().unwrap_or_else(|| "Customer".into()),
        plan: customer.metadata.get("tier").cloned().unwrap_or_default(),   // "tier", not "plan"
        email: customer.email.clone().unwrap_or_default(),
    }
}

pub fn is_enterprise(customer: &stripe::Customer) -> bool {
    customer.metadata.get("plan").is_some_and(|plan| plan == "enterprise")
}
```

## Why it's bad

- The rules for turning a Stripe customer into "our customer" — which metadata key holds the plan, what an
  absent name means — are restated in every function, and have already diverged: one reads `tier`.
- Stripe's types leak into signatures across the codebase, so upgrading the Stripe crate or switching payment
  provider touches every one of them.
- Defaults such as `unwrap_or_default` on the email are decided per call site, so a customer without an email
  is a validation error in one place and an empty recipient in another.

## Better

```rust
pub struct Customer {
    pub name: Option<String>,
    pub email: Email,
    pub plan: Plan,
}

impl TryFrom<&stripe::Customer> for Customer {
    type Error = ImportError;

    fn try_from(raw: &stripe::Customer) -> Result<Self, Self::Error> {
        Ok(Customer {
            name: raw.name.clone(),
            email: raw.email.as_deref().ok_or(ImportError::NoEmail)?.parse()?,
            plan: raw.metadata.get("plan").map(|p| p.parse()).transpose()?.unwrap_or(Plan::Free),
        })
    }
}

pub fn welcome_email(customer: &Customer) -> Email { /* local types only */ }
```

The translation happens once, at the edge, and returns an error for data that does not fit. Everything past
the edge speaks in the program's own types.
