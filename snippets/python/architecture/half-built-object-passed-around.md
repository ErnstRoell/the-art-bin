---
aliases: [missing-builder, object-completed-by-assignment]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [builder, invariants, initialisation, immutability]
keywords: ["= None", "def __init__(self):", ".title =", ".rows =", "obj = ", "setattr("]
signature: "An object is created empty and completed by assigning its attributes one at a time, so every partially built state is an object the type cannot distinguish from a finished one."
distinguish: "Fine for a mutable record whose fields are genuinely optional and independent, where no combination of them is invalid."
added: 2026-09-06
source: refactoring.guru
---

# Half-built object passed around

## Smell

```python
class Report:
    def __init__(self):
        self.title = None
        self.rows = None
        self.totals = None
        self.footer = None

    def render(self):
        return f"{self.title}\n{self.rows}\n{self.totals}\n{self.footer}"


def quarterly(rows):
    report = Report()
    report.title = "Q3"
    report.rows = rows
    report.totals = sum(row.amount for row in rows)
    report.footer = "confidential"
    return report.render()


def preview(rows):
    report = Report()
    report.title = "Preview"
    report.rows = rows[:5]
    return report.render()      # renders "None" for totals and footer, and is not an error
```

## Why it's bad

- `Report()` is a valid call that produces an invalid report, so the type says nothing about whether an
  instance is usable. Every function that receives one has to assume, and one of them will assume wrong.
- The construction sequence is a contract held in the head of whoever wrote the first call site. `preview`
  breaks it and gets a report rendering the string `None`, which reaches a user as a cosmetic bug and gets
  filed against the template.
- Adding a required field cannot be enforced. `__init__` takes no arguments, so the new field defaults to
  `None` at every existing call site and the program keeps running with a hole in it.
- Nothing can be immutable, since the object must stay writable long enough to be finished. Every consumer
  therefore has to consider whether someone else is still assembling it.

## Better

```python
@dataclass(frozen=True)
class Report:
    title: str
    rows: tuple
    totals: int
    footer: str = ""

    def render(self):
        return f"{self.title}\n{self.rows}\n{self.totals}\n{self.footer}"


class ReportBuilder:
    """Holds the partial state, so `Report` never has to."""

    def __init__(self):
        self._title = "Untitled"
        self._rows = ()
        self._footer = ""

    def titled(self, title):
        self._title = title
        return self

    def over(self, rows):
        self._rows = tuple(rows)
        return self

    def confidential(self):
        self._footer = "confidential"
        return self

    def build(self):
        return Report(self._title, self._rows, sum(row.amount for row in self._rows), self._footer)


def preview(rows):
    return ReportBuilder().titled("Preview").over(rows[:5]).build().render()
```

The half-built state still exists, but it lives in the builder and is never handed to anything. A `Report` that
exists is finished, and a new required field is a constructor argument the builder must supply.
