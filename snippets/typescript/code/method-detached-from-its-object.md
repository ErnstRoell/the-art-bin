---
aliases: [unbound-method]
language: typescript
typescript: ">=3.0"
severity: bug
category: correctness
topic: classes
tags: [this, binding, callbacks, events, javascript]
keywords: ["addEventListener(\"click\", this.", ".forEach(this.", ".then(this.", "setTimeout(this.", "onClick={this.", "const { "]
signature: "A method is passed as a callback or destructured off its object, so it is later called without its receiver and this is undefined or some other object."
distinguish: "Fine when the method is an arrow-function property, is bound once, is wrapped in an arrow at the call site, or declares this: void because it never reads this."
added: 2026-09-30
source: typescript-eslint unbound-method
---

# Method detached from its object

## Smell

```typescript
class Counter {
  private count = 0;

  increment(): void {
    this.count++;
  }
}

const counter = new Counter();
button.addEventListener("click", counter.increment);
[1, 2, 3].forEach(counter.increment);
```

## Why it's bad

- A method does not remember its object; `this` is set by how it is called. Class bodies are strict mode, so
  called bare, as `forEach` does, `this` is `undefined` and `this.count++` throws a `TypeError`.
- `addEventListener` calls the handler with `this` set to the element, so the click handler does not throw; it
  quietly increments `button.count` while the counter stays at zero.
- The compiler accepts both lines. typescript-eslint's type-aware `unbound-method` rule is what catches it.

## Better

```typescript
class Counter {
  private count = 0;

  increment = (): void => {
    this.count++;
  };
}

const counter = new Counter();
button.addEventListener("click", counter.increment);
[1, 2, 3].forEach(() => counter.increment());
```
