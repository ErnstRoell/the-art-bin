---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: maintainability
topic: io
tags: [logging, global-state, libraries]
keywords: ["env_logger::init()", "tracing_subscriber::fmt::init()", "set_global_default(", "log::set_logger(", "std::panic::set_hook("]
signature: "Library code installs the process-wide logger, tracing subscriber or panic hook, so the application that uses it loses control of that global and may panic when it sets its own."
distinguish: "Fine in a binary's main, or in a test helper that uses a try_init variant and ignores the error when a logger is already installed."
added: 2026-09-23
source: jeremy-wayland
---

# Library installs a global logger

## Smell

```rust
impl Client {
    pub fn new(config: ClientConfig) -> Self {
        env_logger::init();
        log::info!("client created for {}", config.endpoint);
        Self { config, http: reqwest::Client::new() }
    }
}
```

## Why it's bad

- There is one global logger per process, and it belongs to the application. `env_logger::init` panics if one
  is already set, so an application that configured `tracing` first crashes the moment it creates a `Client`.
- Creating a second `Client` panics for the same reason, which turns an ordinary constructor into one that can
  only be called once.
- Even when it succeeds, the library has chosen the format, filter and destination of every log line in the
  application, including lines that are not its own.

## Better

```rust
impl Client {
    pub fn new(config: ClientConfig) -> Self {
        log::info!("client created for {}", config.endpoint); // emits; the application decides where to
        Self { config, http: reqwest::Client::new() }
    }
}

// in the application's main:
// env_logger::init();
```
