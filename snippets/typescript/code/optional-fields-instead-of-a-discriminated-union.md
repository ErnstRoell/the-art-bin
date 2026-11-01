---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [discriminated-unions, invalid-states, optional-properties, type-design]
keywords: ["loading?: boolean", "data?:", "error?:", "?: ", "isLoading"]
signature: "One interface holds several optional fields that are only meaningful in particular combinations, so the type admits impossible states and the compiler cannot narrow any field from another."
distinguish: "Fine when the optional fields really are independent of one another, such as optional display settings that may each be present or absent in any combination."
added: 2026-09-30
source: Effective TypeScript
---

# Optional fields instead of a discriminated union

## Smell

```typescript
interface RequestState<T> {
  loading?: boolean;
  data?: T;
  error?: Error;
}

function render(state: RequestState<User>) {
  if (state.loading) return <Spinner />;
  if (state.error) return <ErrorBanner error={state.error} />;
  return <Profile user={state.data!} />;
}
```

## Why it's bad

- `{ loading: true, error }`, `{ data, error }`, and `{}` all type-check, so the code must guess which field
  wins, and different components guess differently.
- The type checker cannot learn from `loading` or `error` whether `data` is present, which is why the handbook's
  optional-field `Shape` needed non-null assertions; here `state.data!` renders `Profile` with `undefined` for
  the empty `{}` state.
- Each new field multiplies the combinations, and nothing tells a reader which ones are real.

## Better

```typescript
type RequestState<T> =
  | { status: "loading" }
  | { status: "error"; error: Error }
  | { status: "success"; data: T };

function render(state: RequestState<User>) {
  switch (state.status) {
    case "loading": return <Spinner />;
    case "error": return <ErrorBanner error={state.error} />;
    case "success": return <Profile user={state.data} />;
  }
}
```
