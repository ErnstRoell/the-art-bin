---
aliases: [missing-mediator, peers-calling-peers]
language: python
python: ">=3.0"
severity: taste
category: testability
topic: classes
tags: [mediator, coupling, ui, workflow]
keywords: ["def __init__(self, results", "self._detail", "self._spinner", ".on_submit(", "self._history", "widget"]
signature: "Peer components hold references to each other and call each other directly, so the workflow connecting them exists only as a web of point-to-point calls."
distinguish: "Fine for two components with a genuine ownership relation, where one is a part of the other rather than its peer."
added: 2026-09-06
source: refactoring.guru
---

# Components wired to each other directly

## Smell

```python
class SearchBox:
    def __init__(self, results, history, spinner):
        self._results, self._history, self._spinner = results, history, spinner

    def on_submit(self, text):
        self._spinner.show()
        self._history.push(text)
        self._results.load(text)
        self._spinner.hide()


class ResultList:
    def __init__(self, detail, spinner, status):
        self._detail, self._spinner, self._status = detail, spinner, status

    def on_select(self, item):
        self._spinner.show()
        self._detail.render(item)
        self._status.set(f"showing {item.name}")
        self._spinner.hide()
        self._detail.focus()


class HistoryPanel:
    def __init__(self, search_box):
        self._search_box = search_box      # and the search box holds the history: a cycle

    def on_click(self, text):
        self._search_box.on_submit(text)
```

## Why it's bad

- Each component's constructor is a list of every other component it has to know about. Adding a fourth panel
  means editing the constructors that must now notify it, and the cycle between `SearchBox` and `HistoryPanel`
  means neither can be built first.
- The workflow — submit, record, search, show, focus — is not written anywhere. It is distributed across the
  handlers, so the only way to learn what a search does is to follow calls between three files.
- Nothing is testable in isolation. `SearchBox` needs three collaborators to construct, so a test of "submit
  pushes history" builds a result list and a spinner it does not care about.
- The spinner is shown and hidden in every handler, because "show progress around an interaction" is a
  cross-component rule that has nowhere to live. It presents as a spinner that stays up after the one handler
  that forgot to hide it.

## Better

```python
class SearchScreen:
    """Mediator: the components know it, and nothing else."""

    def __init__(self, search_box, results, detail, history, spinner, status):
        self._parts = (search_box, results, detail, history, spinner, status)
        self._results, self._detail = results, detail
        self._history, self._spinner, self._status = history, spinner, status
        for part in self._parts:
            part.screen = self

    def notify(self, sender, event, value):
        self._spinner.show()
        try:
            if event == "submitted":
                self._history.push(value)
                self._results.load(value)
            elif event == "selected":
                self._detail.render(value)
                self._status.set(f"showing {value.name}")
                self._detail.focus()
        finally:
            self._spinner.hide()


class SearchBox:
    def on_submit(self, text):
        self.screen.notify(self, "submitted", text)


class HistoryPanel:
    def on_click(self, text):
        self.screen.notify(self, "submitted", text)
```

The workflow is one readable method, the spinner rule is stated once, and a component can be tested with a
recording stand-in for `screen` instead of the rest of the screen.
