---
aliases: [path-traversal]
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: io
tags: [path-traversal, filesystem, node, javascript]
keywords: ["path.join(", "path.resolve(", "req.params.", "req.query.", "readFile(", "createReadStream(", "sendFile("]
signature: "A file path is built by joining a request value onto a root directory with no check that the result stays inside it, so ../ segments read or write any file the process can reach."
distinguish: "Fine when the name is first matched against an allow-list or a database record, or when the resolved path is checked to start with the root plus a separator before it is opened."
added: 2026-09-30
source: PortSwigger Web Security Academy
---

# User path joined without containment

## Smell

```typescript
import path from "node:path";
import { readFile } from "node:fs/promises";

const UPLOADS = "/srv/app/uploads";

app.get("/files", async (req, res) => {
  const file = path.join(UPLOADS, String(req.query.name));
  res.send(await readFile(file));
});
```

## Why it's bad

- `path.join` normalises the result, so `?name=../../../etc/passwd` resolves to `/etc/passwd`. Joining is
  string arithmetic, not a security boundary.
- Filtering `../` out of the name is the usual half-fix, and alternative encodings and absolute paths get
  past it; `path.resolve` discards the root outright when a later segment is absolute.
- The check has to compare against the root plus `path.sep`, or `/srv/app/uploads-private/key` passes a
  `startsWith("/srv/app/uploads")` test.

## Better

```typescript
import path from "node:path";
import { readFile } from "node:fs/promises";

const UPLOADS = "/srv/app/uploads";

app.get("/files", async (req, res) => {
  const file = path.resolve(UPLOADS, String(req.query.name));
  if (!file.startsWith(UPLOADS + path.sep)) {
    return res.sendStatus(404);
  }
  res.send(await readFile(file));
});
```
