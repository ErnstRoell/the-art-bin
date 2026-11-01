---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [facade, coupling, setup, teardown, lifecycle]
keywords: ["new Pool(", "await pool.connect()", "client.release()", "new S3Client(", "puppeteer.launch(", "await browser.close()"]
signature: "A handler builds several collaborators of a subsystem it does not own and sequences their setup, ordering and teardown itself, so the same wiring is retyped in every handler."
distinguish: "Fine in a composition root whose whole job is assembling collaborators once, or when a caller genuinely needs fine-grained control and the subsystem also offers the simple path."
added: 2026-09-30
source: refactoring.guru
---

# SDK clients orchestrated in each handler

## Smell

```typescript
app.post("/reports/:id/publish", async (req, res) => {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  const client = await pool.connect();
  const { rows } = await client.query("SELECT * FROM reports WHERE id = $1", [req.params.id]);
  client.release();
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(renderHtml(rows[0]));
  const pdf = await page.pdf({ format: "A4" });
  await browser.close();
  const s3 = new S3Client({ region: "eu-west-1" });
  await s3.send(new PutObjectCommand({ Bucket: BUCKET, Key: `${req.params.id}.pdf`, Body: pdf }));
  res.json({ ok: true });
});

app.post("/reports/:id/email", async (req, res) => {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  const { rows } = await pool.query("SELECT * FROM reports WHERE id = $1", [req.params.id]);
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(renderHtml(rows[0]));
  const pdf = await page.pdf({ format: "Letter" });   // A4 in the other handler
  await mailer.sendMail({ to: req.body.to, attachments: [{ filename: "report.pdf", content: pdf }] });
  res.json({ ok: true });                             // browser and pool never closed
});
```

## Why it's bad

- Each handler is one line of its own subject, publish or email a report, wrapped in a dozen lines assembling
  a database pool, a headless browser and a storage client it does not own.
- The order is a contract nobody states: release the client, close the browser, end the pool. The email
  handler skips all three, which presents as a leaked Chromium per request and pool exhaustion under load.
- The wiring drifts because it is copied: the page size is already A4 in one handler and Letter in the other,
  and nothing can say which is intended.
- Neither handler can be tested without Postgres, Chromium and S3, and replacing Puppeteer means editing
  every route that renders a PDF.

## Better

```typescript
export class ReportService {
  constructor(private db: Pool, private browser: Browser, private s3: S3Client) {}

  /** Owns the order: fetch, render in a fresh page, and close the page even on failure. */
  async pdf(id: string): Promise<Buffer> {
    const { rows } = await this.db.query("SELECT * FROM reports WHERE id = $1", [id]);
    const page = await this.browser.newPage();
    try {
      await page.setContent(renderHtml(rows[0]));
      return await page.pdf({ format: "A4" });
    } finally {
      await page.close();
    }
  }

  async publish(id: string): Promise<void> {
    await this.s3.send(new PutObjectCommand({ Bucket: BUCKET, Key: `${id}.pdf`, Body: await this.pdf(id) }));
  }
}

// built once at startup: const reports = new ReportService(pool, await puppeteer.launch(), s3)
app.post("/reports/:id/publish", async (req, res) => { await reports.publish(req.params.id); res.json({ ok: true }); });
app.post("/reports/:id/email", async (req, res) => {
  await mailer.sendMail({ to: req.body.to, attachments: [{ filename: "report.pdf", content: await reports.pdf(req.params.id) }] });
  res.json({ ok: true });
});
```

The service owns the sequencing and the lifetimes, so the subsystem has one caller instead of one per route,
and a test hands the constructor fakes.
