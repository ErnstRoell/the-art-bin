---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [visitor, double-dispatch, discriminated-unions, expression-problem]
keywords: ["toSvg(): string", "toDxf(): string", "price(rates", "validate(rules", "\"validate\" in", "type Shape = Circle | Square"]
signature: "Each new operation over a stable set of types is added as a method on every one of those classes, so one concern is spread across all of them and each class collects unrelated reasons to change."
distinguish: "Fine when the operation is the type's own behaviour rather than an outside concern, or when the set of types changes faster than the set of operations."
added: 2026-09-30
source: refactoring.guru
---

# Export method added to every shape class

## Smell

```typescript
export class Circle {
  constructor(readonly radius: number) {}
  area(): number { return Math.PI * this.radius ** 2; }
  toSvg(): string { return `<circle r="${this.radius}"/>`; }
  toDxf(): string { return `CIRCLE ${this.radius}`; }
  price(rates: Rates): number { return this.area() * rates.circle; }
  validate(rules: Rules): boolean { return this.radius <= rules.maxRadius; }
}

export class Square {
  constructor(readonly side: number) {}
  area(): number { return this.side ** 2; }
  toSvg(): string { return `<rect width="${this.side}" height="${this.side}"/>`; }
  toDxf(): string { return `POLYLINE ${this.side}`; }
  price(rates: Rates): number { return this.area() * rates.square; }
  // validate: never written
}

export type Shape = Circle | Square;

export function allValid(shapes: Shape[], rules: Rules): boolean {
  return shapes.every((s) => !("validate" in s) || s.validate(rules));   // squares pass unchecked
}
```

## Why it's bad

- The shapes are a stable set and the operations are not. Every new thing anyone wants to do with a shape, a
  second export format, billing, validation, is an edit to every shape class by whoever owns that feature.
- One concern is spread over N classes and no module holds it. Reviewing "how do we price shapes" means
  reading every shape file and hoping to find them all.
- A missing implementation is silent. `Square` has no `validate`, so the caller narrows with an `in` check to
  make it compile, and every square passes validation. That is the presentation: a rule that turned out to
  apply to only some shapes, discovered from production data.
- The geometry classes import the billing rates, the SVG conventions and the validation rules, so a shape
  cannot be used without all of them.

## Better

```typescript
export type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

/** One operation over every shape: the compiler demands a case for each kind. */
export interface ShapeVisitor<R> {
  circle(shape: Extract<Shape, { kind: "circle" }>): R;
  square(shape: Extract<Shape, { kind: "square" }>): R;
}

export function visit<R>(shape: Shape, visitor: ShapeVisitor<R>): R {
  switch (shape.kind) {
    case "circle": return visitor.circle(shape);
    case "square": return visitor.square(shape);
  }
}

// svg.ts: the whole export format, in one place
export const toSvg: ShapeVisitor<string> = {
  circle: (c) => `<circle r="${c.radius}"/>`,
  square: (s) => `<rect width="${s.side}" height="${s.side}"/>`,
};

// validation.ts
export const validator = (rules: Rules): ShapeVisitor<boolean> => ({
  circle: (c) => c.radius <= rules.maxRadius,
  square: (s) => s.side <= rules.maxSide,
});

export const allValid = (shapes: Shape[], rules: Rules) => shapes.every((s) => visit(s, validator(rules)));
```

The shapes are plain data, each concern is one object in one module, and a visitor that forgets a kind does not
compile. Adding a kind is the expensive direction here, a new method on every visitor, which is why this is the
fix only when the kinds are settled and the operations keep arriving.
