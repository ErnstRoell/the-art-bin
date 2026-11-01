---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: testability
topic: classes
tags: [mediator, coupling, ui, workflow]
keywords: ["constructor(private results:", "private spinner: Spinner", "this.spinner.show()", "this.spinner.hide()", "searchBox!: SearchBox", "this.detail.focus()"]
signature: "Peer components take references to each other in their constructors and call each other directly, so the workflow connecting them exists only as a web of point-to-point calls."
distinguish: "Fine for two components with a genuine ownership relation, where one is a part of the other rather than its peer."
added: 2026-09-30
source: refactoring.guru
---

# Components constructed with references to their peers

## Smell

```typescript
export class SearchBox {
  constructor(private results: ResultList, private history: HistoryPanel, private spinner: Spinner) {}

  submit(text: string): void {
    this.spinner.show();
    this.history.push(text);
    this.results.load(text);
    this.spinner.hide();
  }
}

export class ResultList {
  constructor(private detail: DetailPane, private spinner: Spinner, private status: StatusBar) {}

  select(item: Item): void {
    this.spinner.show();
    this.detail.render(item);
    this.status.set(`showing ${item.name}`);
    this.detail.focus();                 // spinner.hide() forgotten here
  }
}

export class HistoryPanel {
  searchBox!: SearchBox;                 // assigned later: SearchBox needs a HistoryPanel first

  push(text: string): void {
    renderEntry(text);
  }

  click(text: string): void {
    this.searchBox.submit(text);
  }
}
```

## Why it's bad

- Each constructor is a list of every other component it has to know about. Adding a panel means editing the
  constructors that must now notify it, and the cycle between `SearchBox` and `HistoryPanel` is papered over
  with a `!` property that is `undefined` until someone remembers to set it.
- The workflow (submit, record, search, show, focus) is written nowhere. It is spread across the handlers, so
  learning what a search does means following calls between files.
- Nothing is testable alone. `SearchBox` needs three collaborators to construct, so a test of "submit records
  history" builds a result list and a spinner it does not care about.
- "Show progress around an interaction" is a cross-component rule with nowhere to live, so each handler repeats
  it and one forgets, leaving a spinner that never goes away.

## Better

```typescript
type ScreenEvent =
  | { type: "submitted"; text: string }
  | { type: "selected"; item: Item };

type Notify = (event: ScreenEvent) => void;

/** Mediator: the components know only `notify`, and the screen knows the workflow. */
export class SearchScreen {
  readonly searchBox = new SearchBox((e) => this.notify(e));
  readonly history = new HistoryPanel((e) => this.notify(e));
  readonly results = new ResultList((e) => this.notify(e));

  constructor(private detail: DetailPane, private spinner: Spinner, private status: StatusBar) {}

  private notify(event: ScreenEvent): void {
    this.spinner.show();
    try {
      switch (event.type) {
        case "submitted":
          this.history.push(event.text);
          this.results.load(event.text);
          break;
        case "selected":
          this.detail.render(event.item);
          this.status.set(`showing ${event.item.name}`);
          this.detail.focus();
          break;
      }
    } finally {
      this.spinner.hide();
    }
  }
}

export class HistoryPanel {
  constructor(private notify: Notify) {}

  click(text: string): void {
    this.notify({ type: "submitted", text });
  }
}
```

The workflow is one readable method, the spinner rule is stated once in a `finally`, the construction cycle is
gone, and a component is tested by passing a function that records what it was told.
