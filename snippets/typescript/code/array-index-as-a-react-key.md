---
aliases: [index-as-key]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [react, keys, lists, state, javascript]
keywords: ["key={index}", "key={i}", "key={idx}", "(item, index) =>", "key={Math.random()}"]
signature: "A React list uses each item's array index as its key, so inserting, removing or reordering items hands one item's component state and DOM to another."
distinguish: "Fine for a static list that is never reordered, filtered, inserted into or deleted from, and whose rows hold no state of their own."
added: 2026-09-30
source: React docs
---

# Array index as a React key

## Smell

```typescript
function TodoList({ todos }: { todos: Todo[] }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>
          <input type="checkbox" defaultChecked={todo.done} />
          {todo.title}
        </li>
      ))}
    </ul>
  );
}
```

## Why it's bad

- React matches elements between renders by key. Add a todo at the top and every index shifts, so the row
  now keyed `0` is the new todo but keeps the old first row's DOM, and its ticked checkbox with it.
- It works while the list only ever grows at the end, which is how it passes review. The bug appears the day
  someone adds sorting, filtering or deletion.
- Omitting the key is the same bug, because React falls back to the index; `key={Math.random()}` is worse,
  recreating every row and losing its input on each render.

## Better

```typescript
function TodoList({ todos }: { todos: Todo[] }) {
  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <input type="checkbox" defaultChecked={todo.done} />
          {todo.title}
        </li>
      ))}
    </ul>
  );
}
```
