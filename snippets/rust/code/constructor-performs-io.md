---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: testability
topic: classes
tags: [constructors, io, dependency-injection]
keywords: ["fn new(", "-> Self {", "TcpStream::connect(", "File::open(", "fs::read_to_string(", "env::var("]
signature: "A new constructor reads files, the environment or the network, so the value cannot be created without its surroundings and failures surface as panics."
distinguish: "Fine for a constructor named for what it does, such as connect, open or from_env, that returns a Result, alongside a plain constructor taking the loaded parts."
added: 2026-09-23
source: jeremy-wayland
---

# Constructor performs I/O

## Smell

```rust
pub struct Mailer {
    smtp: TcpStream,
    from: String,
}

impl Mailer {
    pub fn new() -> Self {
        let host = std::env::var("SMTP_HOST").unwrap();
        let smtp = TcpStream::connect((host.as_str(), 25)).unwrap();
        let from = std::fs::read_to_string("/etc/mailer/from").unwrap();
        Self { smtp, from }
    }
}
```

## Why it's bad

- `Mailer::new()` reads like a cheap, infallible call, which is what `new` means in Rust. It is actually an
  environment read, a network connection and a file read, each of which panics.
- Nothing that holds a `Mailer` can be unit tested without a mail server and that exact file, so the tests
  that exist are the ones that skip it.
- The caller cannot choose the host, the timeout or the sender, and cannot retry a failed connection.

## Better

```rust
impl Mailer {
    pub fn new(smtp: TcpStream, from: String) -> Self {
        Self { smtp, from }
    }

    pub fn connect(host: &str, from: String) -> std::io::Result<Self> {
        Ok(Self::new(TcpStream::connect((host, 25))?, from))
    }
}
```
