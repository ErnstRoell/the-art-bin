---
aliases: [implied-eval]
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: stdlib-misuse
tags: [injection, eval, code-execution, csp, javascript]
keywords: ["eval(", "new Function(", "Function(\"", "setTimeout(`", "setTimeout(\"", "setInterval(\""]
signature: "A string built from input is run as code through eval, the Function constructor or a string passed to setTimeout or setInterval, so the input executes with the caller's privileges."
distinguish: "Fine when data is parsed with JSON.parse instead of evaluated, or when the code string is a build-time constant under the author's control."
added: 2026-09-30
source: MDN
---

# eval or Function constructor on input

## Smell

```typescript
export function evaluateRule(rule: string, order: Order): boolean {
  const check = new Function("order", `return ${rule};`);
  return Boolean(check(order));
}

export function readField(obj: Record<string, unknown>, field: string): unknown {
  return eval(`obj.${field}`);
}

export function scheduleRefresh(widgetId: string): void {
  setTimeout(`refresh("${widgetId}")`, 1000);
}
```

## Why it's bad

- `eval` and `new Function` run the string with the privileges of the caller, so a "rule" or "field" that
  arrives from a request or a config table is arbitrary code in the page or the server process.
- A string first argument to `setTimeout` or `setInterval` is an implied `eval`: a widget id of
  `");steal("` breaks out of the quotes.
- Both are blocked by a strict Content Security Policy, are slower than the alternatives, and stop minifiers
  from renaming anything in reach of the `eval`.

## Better

```typescript
const RULES = new Map<string, (order: Order) => boolean>([
  ["over-100", (order) => order.total > 100],
  ["has-coupon", (order) => order.coupon !== undefined],
]);

export function evaluateRule(rule: string, order: Order): boolean {
  const check = RULES.get(rule);
  if (check === undefined) throw new Error(`unknown rule: ${rule}`);
  return check(order);
}

export function readField(obj: Record<string, unknown>, field: string): unknown {
  return Object.prototype.hasOwnProperty.call(obj, field) ? obj[field] : undefined;
}

export function scheduleRefresh(widgetId: string): void {
  setTimeout(() => refresh(widgetId), 1000);
}
```
