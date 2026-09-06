---
aliases: [missing-command, action-with-nothing-to-undo]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [command, undo, queueing, auditing]
keywords: ["def on_click", "def on_", "_clicked", "doc.text =", "nothing to undo", "self.status("]
signature: "A request is carried out immediately by the handler that received it, so the program holds no object representing the action and cannot undo, queue, log or replay it."
distinguish: "Fine for an action nothing will ever need to reverse, retry or record, such as a read that only refreshes a view."
added: 2026-09-06
source: refactoring.guru
---

# Action invoked with no record of it

## Smell

```python
class ToolBar:
    def on_delete_clicked(self, doc, span):
        doc.text = doc.text[:span.start] + doc.text[span.end:]
        self.status("deleted")

    def on_upper_clicked(self, doc, span):
        chunk = doc.text[span.start:span.end].upper()
        doc.text = doc.text[:span.start] + chunk + doc.text[span.end:]
        self.status("uppercased")

    def on_undo_clicked(self, doc):
        self.status("nothing to undo")      # the only honest thing it can say

    def on_macro_clicked(self, doc, spans):
        for span in spans:                  # no way to say "these three, as one step"
            self.on_delete_clicked(doc, span)
```

## Why it's bad

- The action exists only as the interval during which a method runs. Nothing outlives it, so undo has nothing
  to reverse, an audit log has nothing to record, and a retry has nothing to resend.
- Every capability that treats actions as values is therefore unavailable: no queueing them for a worker, no
  grouping them into one undoable macro, no replaying them against a fresh document in a test.
- The behaviour is welded to the widget. Invoking "delete" from a keyboard shortcut, a script or a test means
  calling a method named `on_delete_clicked` on a toolbar, which is why UI code of this shape ends up
  instantiating widgets in unit tests.
- It presents late and expensively: undo is requested a year in, and there is no small change that adds it,
  because the actions were never things.

## Better

```python
class DeleteText:
    """A command: the action as a value, complete with how to reverse it."""

    def __init__(self, doc, span):
        self._doc, self._span = doc, span
        self._removed = ""

    def do(self):
        text = self._doc.text
        self._removed = text[self._span.start:self._span.end]
        self._doc.text = text[:self._span.start] + text[self._span.end:]

    def undo(self):
        text = self._doc.text
        self._doc.text = text[:self._span.start] + self._removed + text[self._span.start:]


class History:
    def __init__(self):
        self._done = []

    def run(self, command):
        command.do()
        self._done.append(command)

    def undo(self):
        if self._done:
            self._done.pop().undo()


class ToolBar:
    def on_delete_clicked(self, doc, span):
        self._history.run(DeleteText(doc, span))

    def on_undo_clicked(self, doc):
        self._history.undo()
```

Undo, macros, an audit trail and a job queue are now the same feature — a list of commands — and `DeleteText`
is testable without a toolbar.
