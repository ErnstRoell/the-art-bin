---
aliases: [missing-state, state-spread-across-booleans]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: control-flow
tags: [state, invariants, flags, lifecycle]
keywords: ["is_draft", "is_active", "is_closed", "self.is_", "= True", "if self.is_"]
signature: "Several boolean attributes encode one state, so the object can hold combinations no real state corresponds to and every method re-tests the flags."
distinguish: "Fine when the flags are genuinely independent facts about the object rather than one state under different names."
added: 2026-09-06
source: refactoring.guru
---

# State machine encoded in boolean flags

## Smell

```python
class Document:
    def __init__(self):
        self.is_draft = True
        self.is_review = False
        self.is_published = False
        self.is_archived = False

    def submit(self):
        if self.is_archived:
            raise ValueError("archived")
        self.is_draft = False
        self.is_review = True

    def publish(self):
        if not self.is_review and not self.is_draft:   # what state is this asking about?
            raise ValueError("cannot publish")
        self.is_review = False
        self.is_published = True

    def edit(self, text):
        if self.is_published and not self.is_draft:
            raise ValueError("published")
        self.text = text

    def archive(self):
        self.is_archived = True
        self.is_published = False      # is_draft was never cleared by publish
```

## Why it's bad

- Four booleans describe one state, so the object has sixteen representable combinations for four real states.
  Twelve of them are nonsense the type permits, and `archive` leaves the document both draft and archived,
  after which `edit` succeeds on an archived document.
- Every method re-derives the current state from the flags, in its own dialect. `publish` asks "not review and
  not draft" where `edit` asks "published and not draft", and no reader can tell whether those two are meant to
  be the same question.
- Transitions are edits to several fields, so a forgotten line is a silently invalid object rather than an
  error. That is the presentation: not a crash, but a document that reappears in a queue it should have left.
- The legal transitions are nowhere. Nothing in the class says draft goes to review goes to published, so the
  diagram lives in a wiki page and the code is checked against it by hand.

## Better

```python
class State:
    def submit(self, doc):
        raise ValueError(f"cannot submit from {type(self).__name__}")

    def publish(self, doc):
        raise ValueError(f"cannot publish from {type(self).__name__}")

    def edit(self, doc, text):
        raise ValueError(f"cannot edit from {type(self).__name__}")


class Draft(State):
    def submit(self, doc):
        doc.state = Review()

    def edit(self, doc, text):
        doc.text = text


class Review(State):
    def publish(self, doc):
        doc.state = Published()


class Published(State):
    def archive(self, doc):
        doc.state = Archived()


class Archived(State):
    pass


class Document:
    def __init__(self):
        self.state = Draft()

    def submit(self):
        self.state.submit(self)

    def publish(self):
        self.state.publish(self)

    def edit(self, text):
        self.state.edit(self, text)
```

There is one state, so invalid combinations are unrepresentable; each class lists exactly what it permits, so
the transition diagram is the class list; and a forbidden transition raises instead of quietly proceeding.
