---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [strategy, dispatch, modes, function-types]
keywords: ["switch (this.mode)", "this.mode === \"", "mode: Mode", "type Mode = \"", "default: return", "private readonly mode"]
signature: "One mode value is switched on in every method of a class, so a single algorithm is smeared across the class instead of living in one object."
distinguish: "Fine when only one method varies with the mode, where passing that one function or a lookup table at that site is the simpler fix."
added: 2026-09-30
source: refactoring.guru
---

# Mode union switched on in every method

## Smell

```typescript
type Mode = "car" | "walk" | "flight";

export class Route {
  constructor(private readonly mode: Mode, private readonly a: Point, private readonly b: Point) {}

  minutes(): number {
    switch (this.mode) {
      case "car": return (roadKm(this.a, this.b) / 50) * 60;
      case "walk": return (roadKm(this.a, this.b) / 5) * 60;
      default: return (greatCircleKm(this.a, this.b) / 800) * 60;
    }
  }

  waypoints(): Point[] {
    if (this.mode === "car") return roadPath(this.a, this.b);
    if (this.mode === "walk") return footPath(this.a, this.b);
    return [this.a, this.b];
  }

  co2Grams(): number {
    return this.mode === "car" ? roadKm(this.a, this.b) * 120 : 0;   // walking and flying, apparently equal
  }
}

export function fare(mode: Mode, a: Point, b: Point): number {
  return mode === "car" ? roadKm(a, b) * FUEL : TICKET[mode];         // the mode has escaped the class
}
```

## Why it's bad

- Everything that makes a car a car is spread over four places in two modules. Adding `"bike"` means finding
  every test of `mode`, including the one in `fare` nobody remembers.
- The union does not save you. Each branch ends in `default:`, a trailing `return` or a ternary, so the
  compiler sees every method as exhaustive and a bike is silently routed, timed and priced as a flight.
- The branches drift. `co2Grams` has two cases where the others have three, so flying is attributed zero
  emissions by omission rather than by decision, and nothing marks it as a stub.
- A mode cannot be tested alone; each test constructs a `Route` and exercises only the arm it hopes it hit.

## Better

```typescript
interface TravelMode {
  minutes(a: Point, b: Point): number;
  waypoints(a: Point, b: Point): Point[];
  co2Grams(a: Point, b: Point): number;
  fare(a: Point, b: Point): number;
}

const car: TravelMode = {
  minutes: (a, b) => (roadKm(a, b) / 50) * 60,
  waypoints: roadPath,
  co2Grams: (a, b) => roadKm(a, b) * 120,
  fare: (a, b) => roadKm(a, b) * FUEL,
};

const flight: TravelMode = {
  minutes: (a, b) => (greatCircleKm(a, b) / 800) * 60,
  waypoints: (a, b) => [a, b],
  co2Grams: (a, b) => greatCircleKm(a, b) * 250,
  fare: () => TICKET.flight,
};

export const MODES: Record<"car" | "flight", TravelMode> = { car, flight };

export class Route {
  constructor(private readonly mode: TravelMode, private readonly a: Point, private readonly b: Point) {}

  minutes(): number {
    return this.mode.minutes(this.a, this.b);
  }

  fare(): number {
    return this.mode.fare(this.a, this.b);
  }
}
```

One mode is one object literal, so a new mode is one new value checked against `TravelMode`: a missing method
is a compile error rather than a silent zero, and a key missing from `MODES` is one too. When only a single
operation varies, the strategy is just a function-typed parameter and the interface is not needed.
