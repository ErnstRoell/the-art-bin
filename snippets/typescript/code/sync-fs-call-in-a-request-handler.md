---
aliases: [blocking-call-in-request-handler]
language: typescript
typescript: ">=3.0"
severity: trap
category: performance
topic: io
tags: [event-loop, blocking, filesystem, node, server, javascript]
keywords: ["readFileSync(", "writeFileSync(", "existsSync(", "statSync(", "readdirSync(", "execSync(", "(req, res) =>"]
signature: "A synchronous fs call such as readFileSync runs inside a request handler, so the whole Node.js event loop waits on the disk and every other request stalls."
distinguish: "Fine at startup or in a command-line script, such as reading config once before the server listens, where nothing else is waiting on the event loop."
added: 2026-09-30
source: Node.js "Don't Block the Event Loop" guide
---

# Sync fs call in a request handler

## Smell

```typescript
import { readFileSync } from "node:fs";

app.get("/report", (req, res) => {
  const template = readFileSync("templates/report.html", "utf8");
  const rows = JSON.parse(readFileSync("data/latest.json", "utf8"));
  res.send(render(template, rows));
});
```

## Why it's bad

- The synchronous fs APIs block the event loop and all further JavaScript until they complete. While one
  request reads the disk, no other request in the process makes progress.
- It is fast on a laptop SSD and bites in production: file access times vary widely, especially on network
  file systems such as NFS, and the stall multiplies under concurrent load.
- The Node.js guide says these APIs exist for scripting convenience and are not intended for use in a server;
  the same goes for `execSync`, `zlib.*Sync` and `crypto.pbkdf2Sync`.

## Better

```typescript
import { readFile } from "node:fs/promises";

app.get("/report", async (req, res, next) => {
  try {
    const [template, raw] = await Promise.all([
      readFile("templates/report.html", "utf8"),
      readFile("data/latest.json", "utf8"),
    ]);
    res.send(render(template, JSON.parse(raw)));
  } catch (err) {
    next(err);
  }
});
```
