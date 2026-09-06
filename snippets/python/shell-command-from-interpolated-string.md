---
aliases: [shell-true-injection, os-system-interpolation]
language: python
python: ">=3.5"
severity: bug
category: security
topic: io
tags: [injection, subprocess, shell]
keywords: ["shell=True", "os.system(", "subprocess.run(f", "os.popen(", "check=True"]
signature: "A shell command is built by interpolating a value into a string and executed through a shell."
distinguish: "Fine when the arguments are passed as a list without a shell, or when the command is a fixed literal with no interpolation."
added: 2026-09-04
source: ernst
---

# Shell command from an interpolated string

## Smell

```python
def archive(name):
    subprocess.run(f"tar czf {name}.tar.gz {name}", shell=True, check=True)


archive(request.form["dataset"])
```

## Why it's bad

- With `shell=True` the string is parsed by `/bin/sh`, so `;`, `|`, `&&`, backticks, and `$()` in `name` are
  operators rather than characters — `archive("x; rm -rf ~")` runs two commands.
- Quoting is not a fix. Every escaping scheme written by hand has a bypass, which is why `shlex.quote` exists
  and why avoiding the shell entirely is cheaper than using it correctly.
- Even with trusted input the shell is an extra interpreter between the code and the process: a name containing
  a space silently becomes two arguments and the command fails in a way the traceback cannot explain.
- Passing a list skips the shell altogether, so the argument boundary is decided by Python rather than by the
  contents of the string.

## Better

```python
def archive(name):
    subprocess.run(["tar", "czf", f"{name}.tar.gz", name], check=True)
```
