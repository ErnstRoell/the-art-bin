# Taxonomy

The two closed lists every smell is filed against. `category` says what a smell costs you; `topic` says which
part of Python it lives in. Both are validated, so a value not listed here fails CI.

Adding a value is a deliberate change to this file, not something done in passing. Before adding one, check that
no existing value fits — a taxonomy that grows per contribution stops being able to answer questions.

## Category

What the smell costs you. Exactly one per smell.

- `correctness` — the code produces wrong results, now or under a foreseeable condition
- `security` — the code exposes a vulnerability
- `performance` — the code is measurably slower or heavier than the obvious alternative
- `readability` — the code is harder to understand than it needs to be
- `maintainability` — the code makes future change riskier or more expensive
- `testability` — the code is harder to test than it needs to be

There is deliberately no `style` category. That axis is carried by `severity: taste`.

## Topic

Which Python feature the smell lives in. Exactly one per smell.

- `exceptions` — raising, catching, and error propagation
- `mutability` — shared mutable state, aliasing, in-place modification
- `typing` — annotations, type checking, protocols
- `naming` — identifier choice
- `functions` — signatures, parameters, return values, scope
- `classes` — class design, inheritance, attributes, methods
- `control-flow` — conditionals, loops, comprehension structure, early returns
- `imports` — import mechanics and module structure
- `strings` — string construction, formatting, encoding
- `io` — files, paths, sockets, subprocesses
- `concurrency` — threads, async, locks, timing
- `stdlib-misuse` — standard library APIs used against their design

`stdlib-misuse` is a deliberate escape hatch, so contributors are not forced into a bad fit. If it grows past
roughly 15% of the corpus, split it into more specific topics.

## Severity

Not extensible — these three values are fixed.

- `bug` — wrong today; produces incorrect behaviour as written
- `trap` — works today, bites later; correct until a condition changes, then fails surprisingly
- `taste` — works and keeps working, but reads badly
