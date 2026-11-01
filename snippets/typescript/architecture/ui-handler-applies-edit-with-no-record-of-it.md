---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [command, undo, history, closures]
keywords: ["addEventListener(\"click\"", "editor.text =", "editor.text.slice(", "\"nothing to undo\"", "onKeyDown(", "event.key ==="]
signature: "A request is carried out immediately by the event handler that received it, so the program holds no value representing the action and cannot undo, queue, log or replay it."
distinguish: "Fine for an action nothing will ever need to reverse, retry or record, such as a click that only toggles a panel open."
added: 2026-09-30
source: refactoring.guru
---

# UI handler applies edit with no record of it

## Smell

```typescript
export function wireToolbar(editor: Editor, toolbar: HTMLElement): void {
  toolbar.querySelector("#delete")!.addEventListener("click", () => {
    const { start, end } = selection();
    editor.text = editor.text.slice(0, start) + editor.text.slice(end);
    status("deleted");
  });

  toolbar.querySelector("#upper")!.addEventListener("click", () => {
    const { start, end } = selection();
    const chunk = editor.text.slice(start, end).toUpperCase();
    editor.text = editor.text.slice(0, start) + chunk + editor.text.slice(end);
    status("uppercased");
  });

  toolbar.querySelector("#undo")!.addEventListener("click", () => {
    status("nothing to undo");             // the only honest thing it can say
  });
}

export function onKeyDown(editor: Editor, event: KeyboardEvent): void {
  if (event.ctrlKey && event.key === "Backspace") {
    const { start, end } = selection();    // the delete handler, retyped for the shortcut
    editor.text = editor.text.slice(0, start) + editor.text.slice(end);
  }
}
```

## Why it's bad

- The action exists only while a closure runs. Nothing outlives it, so undo has nothing to reverse, an audit
  log has nothing to record and a retry has nothing to resend.
- The toolbar button and the keyboard shortcut are two copies of "delete", because the behaviour has no
  existence outside the listener that performs it. The copies drift, and only one of them sets the status.
- Every feature that treats actions as values is out of reach: grouping three edits into one undo step,
  sending edits to a collaborator, replaying them against a fresh document in a test.
- Testing an edit means building a DOM and dispatching a click, since the listener is the only handle on it.

## Better

```typescript
/** A command: the action as a value, complete with how to reverse it. */
interface Command {
  apply(editor: Editor): void;
  revert(editor: Editor): void;
}

const deleteRange = (start: number, end: number): Command => {
  let removed = "";
  return {
    apply(editor) {
      removed = editor.text.slice(start, end);
      editor.text = editor.text.slice(0, start) + editor.text.slice(end);
    },
    revert(editor) {
      editor.text = editor.text.slice(0, start) + removed + editor.text.slice(start);
    },
  };
};

export class History {
  private readonly done: Command[] = [];

  constructor(private readonly editor: Editor) {}

  run(command: Command): void {
    command.apply(this.editor);
    this.done.push(command);
  }

  undo(): void {
    const last = this.done.pop();
    if (last) last.revert(this.editor);
  }
}

// Every entry point produces the same command:
deleteButton.addEventListener("click", () => history.run(deleteRange(...bounds())));
undoButton.addEventListener("click", () => history.undo());
```

Undo, macros and an audit trail are now the same feature, a list of commands, and `deleteRange` is testable
against a plain `Editor` with no DOM at all.
