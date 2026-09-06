---
aliases: [missing-facade, subsystem-assembled-inline]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [facade, dispatch, coupling, composition-root, lifecycle]
keywords: [".connect()", ".close()", "= Client(", "= Repository(", "= Mailer(", "boto3.client", "Session("]
signature: "A caller builds several collaborators of a subsystem it does not own and sequences their setup, ordering and teardown itself, so the same wiring is retyped at every call site."
distinguish: "Fine in a composition root, whose whole job is assembling collaborators once and handing them to the code that uses them."
added: 2026-09-06
source: ernst
---

# Subsystem wired up at every call site

## Smell

```python
def export_report(order_id):
    db = Database(DB_URL)
    db.connect()
    order = OrderRepository(db).fetch(order_id)
    renderer = PdfRenderer(font="Helvetica")
    renderer.load_fonts()
    pdf = renderer.render(order.lines)
    key = f"reports/{order_id}.pdf"
    S3Client(BUCKET, region="eu-west-1").upload(key, pdf)
    db.close()
    return key


def email_report(order_id, address):
    db = Database(DB_URL)
    db.connect()
    order = OrderRepository(db).fetch(order_id)
    renderer = PdfRenderer(font="Times")
    pdf = renderer.render(order.lines)
    Mailer(SMTP_HOST).send(address, "Your report", pdf)
    return True
```

## Why it's bad

- Each function is one line of its own subject — export a report, email a report — wrapped in a dozen lines of
  assembling four parts it does not own. The intent is not hard to find because the code is long; it is hard to
  find because the wiring and the intent are at the same level of detail.
- The order is a contract nobody states: `connect` before `fetch`, `load_fonts` before `render`, `close` after.
  `email_report` breaks two of the three, and both breakages are invisible where they happen — the missing
  `load_fonts` presents as a rendering diff in one code path, the missing `close` as pool exhaustion under load
  that gets blamed on traffic.
- The wiring is duplicated rather than shared, so it drifts. The font is already `Helvetica` in one function and
  `Times` in the other, and nothing in the program can compare those two answers or say which is intended.
- Every subsystem is constructed inline, so neither function can be tested without a database, an S3 bucket and
  an SMTP host. This is `constructor-does-io` seen from the calling side: the call site, not the constructor, is
  what nails the collaborators down.
- Any change to the subsystem — a renderer that needs a cache, a storage client that needs a session — is a
  `grep` for every site that assembles it, and the sites are only findable by recognising the shape.
- This is the case a facade exists for: one object that owns the sequencing, so the subsystem has one caller
  instead of one per feature. See `kwargs-forwarded-through-layers` for the other common answer to the same
  pressure, which is to pass the whole subsystem down instead of hiding it.

## Better

```python
class ReportService:
    """Facade: the one place that knows how these four parts fit together."""

    def __init__(self, orders, renderer, store, mailer):
        self._orders = orders
        self._renderer = renderer
        self._store = store
        self._mailer = mailer

    def _render(self, order_id):
        return self._renderer.render(self._orders.fetch(order_id).lines)

    def export(self, order_id):
        key = f"reports/{order_id}.pdf"
        self._store.upload(key, self._render(order_id))
        return key

    def email(self, order_id, address):
        self._mailer.send(address, "Your report", self._render(order_id))


def export_report(order_id, reports):
    return reports.export(order_id)


def email_report(order_id, address, reports):
    reports.email(order_id, address)


# Assembled once, at start-up, by the code that owns the process:
#     reports = ReportService(
#         OrderRepository(db),
#         PdfRenderer.with_fonts("Helvetica"),
#         S3Client(BUCKET, region="eu-west-1"),
#         Mailer(SMTP_HOST),
#     )
```

The facade takes collaborators already built, so the order that used to be a convention is now either enforced
by a constructor (`PdfRenderer.with_fonts`) or held in one method. Both call sites shrink to the sentence they
were always meant to be, the font exists once, and a test hands `ReportService` four fakes.
