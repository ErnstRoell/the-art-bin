---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: testability
topic: classes
tags: [mediator, rc, refcell, coupling, events]
keywords: ["Rc<RefCell<", "Weak<RefCell<", ".borrow_mut().", "Option<Rc<RefCell<", "already borrowed", "upgrade().unwrap()"]
signature: "Peer components hold Rc RefCell handles to each other and call each other directly, so the workflow connecting them exists only as a web of point-to-point calls checked at runtime."
distinguish: "Fine for a genuinely shared graph such as a scene tree or document model, where the links are the data rather than a workflow between components."
added: 2026-09-23
source: refactoring.guru
---

# Peers wired together with Rc RefCell

## Smell

```rust
pub struct SearchBox {
    text: String,
    results: Option<Rc<RefCell<ResultsList>>>,
    status: Option<Rc<RefCell<StatusBar>>>,
}

pub struct ResultsList {
    items: Vec<Hit>,
    search: Option<Weak<RefCell<SearchBox>>>,
    status: Option<Rc<RefCell<StatusBar>>>,
}

impl SearchBox {
    pub fn on_input(&mut self, text: &str, index: &Index) {
        self.text = text.to_owned();
        let hits = index.search(text);
        self.status.as_ref().unwrap().borrow_mut().show(&format!("{} results", hits.len()));
        self.results.as_ref().unwrap().borrow_mut().set_items(hits);
    }
}

impl ResultsList {
    pub fn set_items(&mut self, items: Vec<Hit>) {
        self.items = items;
        if self.items.is_empty() {
            // clear the search box: panics, it is already mutably borrowed by on_input
            let search = self.search.as_ref().unwrap().upgrade().unwrap();
            search.borrow_mut().text.clear();
        }
    }
}
```

## Why it's bad

- The borrow checker cannot see a web of `Rc<RefCell<>>`, so it moves the check to runtime. `set_items`
  borrowing the search box while `on_input` is still inside it is a `BorrowMutError` panic, found by typing a
  query with no results.
- Each component knows the concrete type of every other one. Adding a filter panel means editing all of them
  and deciding who holds strong and who holds weak references to avoid a leak.
- The actual workflow — input produces results, results update status — is not written down anywhere; it is
  spread across method bodies in three types.
- Unit testing one component means constructing all three and wiring the cycle first.

## Better

```rust
pub enum UiEvent {
    QueryChanged(String),
    ResultsReady(Vec<Hit>),
}

pub struct SearchScreen {
    search: SearchBox,
    results: ResultsList,
    status: StatusBar,
    index: Index,
}

impl SearchScreen {
    pub fn handle(&mut self, event: UiEvent) {
        match event {
            UiEvent::QueryChanged(text) => {
                self.search.set_text(&text);
                let hits = self.index.search(&text);
                self.handle(UiEvent::ResultsReady(hits));
            }
            UiEvent::ResultsReady(hits) => {
                self.status.show(&format!("{} results", hits.len()));
                if hits.is_empty() {
                    self.search.clear();
                }
                self.results.set_items(hits);
            }
        }
    }
}
```

The screen owns its components outright, so the borrow checker sees every access again, and the workflow is
one `match` a reader can follow.
