---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: control-flow
tags: [state, state-machine, enums, typestate]
keywords: ["is_connected: bool", "is_authenticated: bool", "Option<TcpStream>", "token: Option<String>", "if self.is_", ".as_mut().unwrap()"]
signature: "Several bool and Option fields together encode one lifecycle state, so the struct can hold combinations no real state corresponds to and every method re-checks them."
distinguish: "Fine when the flags are genuinely independent features that can be combined freely, so every combination is a valid state."
added: 2026-09-23
source: refactoring.guru
---

# State machine as struct flags

## Smell

```rust
pub struct Connection {
    is_connected: bool,
    is_authenticated: bool,
    stream: Option<TcpStream>,
    token: Option<String>,
}

impl Connection {
    pub fn authenticate(&mut self, password: &str) -> io::Result<()> {
        if !self.is_connected {
            return Err(io::Error::other("not connected"));
        }
        let token = login(self.stream.as_mut().unwrap(), password)?;
        self.token = Some(token);
        self.is_authenticated = true;
        Ok(())
    }

    pub fn send(&mut self, data: &[u8]) -> io::Result<()> {
        if !self.is_connected || !self.is_authenticated {
            return Err(io::Error::other("not ready"));
        }
        self.stream.as_mut().unwrap().write_all(data)
    }

    pub fn disconnect(&mut self) {
        self.stream = None;
        self.is_connected = false;
        // is_authenticated and token left behind
    }
}
```

## Why it's bad

- Two bools and two options give sixteen combinations for three real states. `disconnect` forgets to clear
  authentication, so a reconnect is treated as authenticated with a stale token.
- `stream.as_mut().unwrap()` is an assertion that the flags and the option agree, which nothing enforces; the
  first time they disagree it panics.
- Every method opens with its own check of the flags, and each check is a chance to test the wrong subset.
  Adding a state such as `Reconnecting` means auditing all of them.
- Rust's enums can make the invalid combinations unrepresentable, and this is the code that does not use them.

## Better

```rust
pub enum Connection {
    Disconnected,
    Connected { stream: TcpStream },
    Authenticated { stream: TcpStream, token: String },
}

impl Connection {
    pub fn authenticate(self, password: &str) -> Result<Self, (Self, io::Error)> {
        match self {
            Connection::Connected { mut stream } => match login(&mut stream, password) {
                Ok(token) => Ok(Connection::Authenticated { stream, token }),
                Err(e) => Err((Connection::Connected { stream }, e)),
            },
            other => Err((other, io::Error::other("not connected"))),
        }
    }

    pub fn send(&mut self, data: &[u8]) -> io::Result<()> {
        match self {
            Connection::Authenticated { stream, .. } => stream.write_all(data),
            _ => Err(io::Error::other("not authenticated")),
        }
    }

    pub fn disconnect(&mut self) {
        *self = Connection::Disconnected; // the token goes with the state that owned it
    }
}
```

The stream exists exactly when the connection is up, the token exactly when it is authenticated, and a new
state is a new variant that every `match` is told about.
