---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: performance
topic: classes
tags: [singleton, connection-pool, shared-resources, arc]
keywords: ["reqwest::Client::new()", "PgPool::connect(", "Client::builder()", "Pool::new(", "Regex::new(", "fn handler("]
signature: "A client, pool or other expensive shared resource is constructed afresh inside each function that needs it, so every call pays the setup cost and the instances share nothing."
distinguish: "Fine when the resource is cheap and stateless, or when isolation between calls is the point, such as a fresh client per test."
added: 2026-09-23
source: refactoring.guru
---

# Expensive client built per call

## Smell

```rust
pub async fn fetch_weather(city: &str) -> reqwest::Result<Weather> {
    let client = reqwest::Client::new();
    client.get(format!("{WEATHER_API}/{city}")).send().await?.json().await
}

pub async fn save_reading(reading: &Reading) -> sqlx::Result<()> {
    let pool = PgPool::connect(&std::env::var("DATABASE_URL").unwrap()).await?;
    sqlx::query("INSERT INTO readings (city, temp) VALUES ($1, $2)")
        .bind(&reading.city)
        .bind(reading.temp)
        .execute(&pool)
        .await?;
    Ok(())
}
```

## Why it's bad

- `reqwest::Client` holds a connection pool and TLS configuration; a new one per call means a fresh TCP and
  TLS handshake per request, where a shared client would reuse a warm connection.
- A new `PgPool` per insert opens new database connections every time, so under load the service exhausts the
  database's connection limit while each pool sits nearly empty.
- The resources cannot share anything they were designed to share — pooled connections, DNS caches, rate
  limits — because each instance lives for one call.
- The usual over-correction is a global `static`, which trades this for `global-static-for-shared-state`.

## Better

```rust
#[derive(Clone)]
pub struct AppState {
    http: reqwest::Client,   // cheap to clone: an Arc inside
    db: PgPool,              // likewise
}

impl AppState {
    pub async fn new(database_url: &str) -> sqlx::Result<Self> {
        Ok(Self { http: reqwest::Client::new(), db: PgPool::connect(database_url).await? })
    }

    pub async fn fetch_weather(&self, city: &str) -> reqwest::Result<Weather> {
        self.http.get(format!("{WEATHER_API}/{city}")).send().await?.json().await
    }

    pub async fn save_reading(&self, reading: &Reading) -> sqlx::Result<()> {
        sqlx::query("INSERT INTO readings (city, temp) VALUES ($1, $2)")
            .bind(&reading.city)
            .bind(reading.temp)
            .execute(&self.db)
            .await?;
        Ok(())
    }
}
```

Built once where the process starts and passed down, so there is one of each without a global, and tests
construct their own.
