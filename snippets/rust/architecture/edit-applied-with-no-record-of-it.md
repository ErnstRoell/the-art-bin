---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [command, undo, history, enums]
keywords: ["fn on_key(", "self.text.insert_str(", "self.text.replace_range(", "fn undo(", "match key {", "history: Vec<"]
signature: "A request is carried out immediately by the handler that received it, so the program holds no value representing the action and cannot undo, queue, log or replay it."
distinguish: "Fine when the action is genuinely fire-and-forget and nobody will ever need to undo, retry, audit or batch it."
added: 2026-09-23
source: refactoring.guru
---

# Edit applied with no record of it

## Smell

```rust
pub struct Editor {
    text: String,
    cursor: usize,
    clipboard: String,
}

impl Editor {
    pub fn on_key(&mut self, key: Key) {
        match key {
            Key::Char(c) => {
                self.text.insert(self.cursor, c);
                self.cursor += c.len_utf8();
            }
            Key::Backspace if self.cursor > 0 => {
                let prev = self.text[..self.cursor].chars().next_back().unwrap();
                self.cursor -= prev.len_utf8();
                self.text.remove(self.cursor);
            }
            Key::Paste => {
                self.text.insert_str(self.cursor, &self.clipboard);
                self.cursor += self.clipboard.len();
            }
            _ => {}
        }
    }

    pub fn undo(&mut self) {
        // what happened last? nothing recorded it
    }
}
```

## Why it's bad

- Each edit exists only as the lines that performed it. Once `on_key` returns, nothing knows a paste
  happened, so `undo` has nothing to work from.
- Every feature built on actions — undo, redo, macros, collaborative sync, an audit log — has to be threaded
  through every arm of the handler, by hand, for every key.
- A menu item and a keyboard shortcut that both paste have to call into the handler or duplicate its body,
  because the action has no existence outside it.
- Testing an edit requires synthesising the key event, since the key is the only handle on the behaviour.

## Better

```rust
pub enum Edit {
    Insert { at: usize, text: String },
    Delete { at: usize, text: String },
}

impl Edit {
    fn apply(&self, doc: &mut String) {
        match self {
            Edit::Insert { at, text } => doc.insert_str(*at, text),
            Edit::Delete { at, text } => doc.replace_range(*at..*at + text.len(), ""),
        }
    }

    fn inverse(&self) -> Edit {
        match self {
            Edit::Insert { at, text } => Edit::Delete { at: *at, text: text.clone() },
            Edit::Delete { at, text } => Edit::Insert { at: *at, text: text.clone() },
        }
    }
}

impl Editor {
    pub fn perform(&mut self, edit: Edit) {
        edit.apply(&mut self.text);
        self.history.push(edit);
    }

    pub fn undo(&mut self) {
        if let Some(edit) = self.history.pop() {
            edit.inverse().apply(&mut self.text);
        }
    }
}
```

Key handling now only translates a key into an `Edit`. The edit is a value that can be stored, inverted,
sent over the wire or replayed, and every entry point produces the same one.
