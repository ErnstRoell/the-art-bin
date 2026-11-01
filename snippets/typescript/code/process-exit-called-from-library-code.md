---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: maintainability
topic: functions
tags: [process, exit, error-handling, cli, node, javascript]
keywords: ["process.exit(", "process.exit(1)", "process.exit(0)", "exit(1)"]
signature: "A function below the program's entry point calls process.exit on failure, so callers cannot recover and pending output such as the error message itself can be lost."
distinguish: "Fine in the top-level entry point of a command-line program that owns the process, preferably by setting process.exitCode and letting the process end on its own."
added: 2026-09-30
source: Node.js process docs
---

# process.exit called from library code

## Smell

```typescript
import { existsSync, readFileSync } from "node:fs";

export function loadConfig(path: string): Config {
  if (!existsSync(path)) {
    console.error(`config file not found: ${path}`);
    process.exit(1);
  }
  const config = JSON.parse(readFileSync(path, "utf8"));
  if (!config.apiKey) {
    console.error("config is missing apiKey");
    process.exit(1);
  }
  return config;
}
```

## Why it's bad

- `process.exit()` ends the process as quickly as possible even with I/O still pending, including writes to
  stdout and stderr, which may be asynchronous. The message explaining the exit is the output most likely to
  be truncated.
- No caller can catch it. A server that reloads config on a signal dies instead of keeping the old config, and
  a test that exercises the failure path takes the whole test runner down with it.
- The Node.js docs recommend setting `process.exitCode` and letting the process exit naturally, or throwing,
  which leaves the decision with whoever owns the process.

## Better

```typescript
import { existsSync, readFileSync } from "node:fs";

export class ConfigError extends Error {}

export function loadConfig(path: string): Config {
  if (!existsSync(path)) throw new ConfigError(`config file not found: ${path}`);
  const config = JSON.parse(readFileSync(path, "utf8"));
  if (!config.apiKey) throw new ConfigError("config is missing apiKey");
  return config;
}

// bin/cli.ts: only the entry point decides how the process ends
try {
  run(loadConfig(process.argv[2]));
} catch (err) {
  console.error(err instanceof Error ? err.message : err);
  process.exitCode = 1;
}
```
