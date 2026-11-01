---
aliases: []
language: rust
rust: ">=1.39"
severity: trap
category: performance
topic: concurrency
tags: [async, tokio, blocking, executor]
keywords: ["async fn", "std::fs::", "std::thread::sleep", "reqwest::blocking", ".lock().unwrap()", "std::net::TcpStream"]
signature: "An async function calls blocking file, network or sleep APIs from the standard library, so the executor thread stalls and every task scheduled on it waits."
distinguish: "Fine when the blocking call is moved onto spawn_blocking or a dedicated thread, or when it is a short uncontended lock or a read so small it never waits in practice."
added: 2026-09-23
source: jeremy-wayland
---

# Blocking I/O in async task

## Smell

```rust
async fn handle(req: Request) -> Response {
    let template = std::fs::read_to_string("templates/page.html").unwrap();
    let user = reqwest::blocking::get(user_url(&req)).unwrap().text().unwrap();
    std::thread::sleep(std::time::Duration::from_millis(50)); // crude rate limit
    render(&template, &user)
}
```

## Why it's bad

- An async runtime runs many tasks on a few threads, and it can only switch tasks at an `.await`. None of
  these calls has one, so the worker is held for the full disk read, HTTP round trip and sleep.
- Every other request queued on that worker waits too. The symptom is latency that rises with load for no
  visible reason, with low CPU and no errors.
- `reqwest::blocking` inside a Tokio runtime goes further and panics with "Cannot drop a runtime in a context
  where blocking is not allowed", but only on the path that reaches it.

## Better

```rust
async fn handle(req: Request, client: &reqwest::Client) -> Result<Response, AppError> {
    let template = tokio::fs::read_to_string("templates/page.html").await?;
    let user = client.get(user_url(&req)).send().await?.text().await?;
    tokio::time::sleep(std::time::Duration::from_millis(50)).await;
    Ok(render(&template, &user))
}
```

Work with no async equivalent, such as heavy CPU or a synchronous database driver, goes through
`tokio::task::spawn_blocking` instead.
