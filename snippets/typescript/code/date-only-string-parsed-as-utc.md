---
aliases: [new-date-iso-date-off-by-one-day]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: stdlib-misuse
tags: [dates, time-zones, parsing, javascript]
keywords: ["new Date(\"", "new Date(isoDate)", "Date.parse(", "toLocaleDateString(", ".getDate()"]
signature: "A calendar date string such as 2024-03-10 is passed to new Date, which reads date-only forms as UTC midnight and so shows the previous day in any time zone west of UTC."
distinguish: "Fine when the value is meant as an instant and is only compared or formatted in UTC, or when the string carries an explicit offset such as a trailing Z."
added: 2026-09-30
source: MDN
---

# Date-only string parsed as UTC

## Smell

```typescript
function formatDueDate(isoDate: string): string {
  // isoDate comes from <input type="date">, such as "2024-03-10"
  return new Date(isoDate).toLocaleDateString("en-US");
}

function dueDayOfMonth(isoDate: string): number {
  return new Date(isoDate).getDate();
}

// In New York: formatDueDate("2024-03-10") is "3/9/2024", dueDayOfMonth is 9
```

## Why it's bad

- Without an offset, date-only forms are parsed as UTC while date-time forms are parsed as local time. MDN
  describes the UTC reading as a historical spec error, inconsistent with ISO 8601, kept for web compatibility.
- UTC midnight is the previous evening anywhere west of UTC, so local getters and `toLocaleDateString` report
  the day before. Tests pass on a CI machine running in UTC and fail for users in the Americas.
- `"2024-03-10"` and `"2024-03-10T00:00"` look interchangeable but parse to instants hours apart, so code that
  mixes the two compares dates that are not the same day.

## Better

```typescript
function parseCalendarDate(isoDate: string): Date {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day); // components are read in local time
}

function formatDueDate(isoDate: string): string {
  return parseCalendarDate(isoDate).toLocaleDateString("en-US");
}
```
