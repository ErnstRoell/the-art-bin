---
aliases: [sleep-then-assert, arbitrary-wait]
language: typescript
typescript: ">=3.0"
severity: trap
category: testability
topic: concurrency
tags: [timers, flaky-tests, async, javascript]
keywords: ["setTimeout(resolve", "new Promise((r) => setTimeout", "sleep(", "waitForTimeout", "await delay("]
signature: "Code waits a fixed number of milliseconds and then assumes an asynchronous operation has finished, instead of waiting on the operation or a condition it produces."
distinguish: "Fine for deliberate delays such as backoff between retries or a rate limit, and under fake timers where advancing the clock is the thing being tested."
added: 2026-09-30
source: Playwright docs
---

# setTimeout in place of synchronisation

## Smell

```typescript
test("saving shows a confirmation", async () => {
  render(<ProfileForm />);
  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await new Promise((resolve) => setTimeout(resolve, 500));

  expect(screen.getByText("Saved")).toBeInTheDocument();
});
```

## Why it's bad

- The 500 ms is a guess about how long the save takes. Node.js makes no guarantee about when a timer fires,
  and a loaded CI machine or a slower mock turns the guess into an intermittent failure.
- When the guess is generous, every run pays the full delay even though the work finished in a few
  milliseconds, and the suite gets slower one sleep at a time.
- Playwright's docs put it bluntly: tests that wait for time are inherently flaky; wait on signals such as
  events or elements appearing instead.

## Better

```typescript
test("saving shows a confirmation", async () => {
  render(<ProfileForm />);
  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  expect(await screen.findByText("Saved")).toBeInTheDocument();
});
```

`findBy` queries and `waitFor` retry until the condition holds or a timeout expires, so the test waits exactly
as long as it needs to. Outside tests, await the promise or event the work produces.
