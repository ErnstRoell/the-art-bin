---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: security
topic: strings
tags: [injection, sql, sqlx, database]
keywords: ['query(&format!(', 'format!("SELECT', 'format!("DELETE', "WHERE name = '{}'", "execute(&format!(", "push_str(\" AND"]
signature: "A SQL statement is assembled by formatting values into the query text, so a value containing SQL is executed as SQL."
distinguish: "Fine when only identifiers chosen from a fixed allow-list, such as a sort column matched from an enum, are formatted in and every value is bound as a parameter."
added: 2026-09-23
source: jeremy-wayland
---

# SQL assembled with format

## Smell

```rust
pub async fn find_user(pool: &PgPool, email: &str) -> sqlx::Result<Option<User>> {
    sqlx::query_as::<_, User>(&format!("SELECT * FROM users WHERE email = '{email}'"))
        .fetch_optional(pool)
        .await
}
```

## Why it's bad

- An email of `' OR '1'='1` returns the first user in the table, and `'; DROP TABLE users; --` does what it
  says on drivers that accept multiple statements.
- A legitimate value with an apostrophe, such as `o'brien@example.com`, is a syntax error, which is usually
  how the bug is found first.
- Every distinct value is a distinct statement, so the database cannot reuse a prepared plan, and the
  compile-time checking of `sqlx::query!` is unavailable.

## Better

```rust
pub async fn find_user(pool: &PgPool, email: &str) -> sqlx::Result<Option<User>> {
    sqlx::query_as::<_, User>("SELECT * FROM users WHERE email = $1")
        .bind(email)
        .fetch_optional(pool)
        .await
}
```
