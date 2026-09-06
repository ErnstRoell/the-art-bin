---
aliases: [missing-visitor, concern-spread-across-a-hierarchy]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [visitor, double-dispatch, separation-of-concerns, expression-problem]
keywords: ["def to_svg(self)", "def to_json(self)", "def price(self", "def validate(self", "class Circle", "def accept("]
signature: "Each new operation over a stable set of types is added as a method on every one of those types, so one concern is spread across all of them and each class collects unrelated reasons to change."
distinguish: "Fine when the operation is the type's own behaviour rather than an outside concern, or when the set of types changes faster than the set of operations."
added: 2026-09-06
source: refactoring.guru
---

# Operation added to every class in a hierarchy

## Smell

```python
class Circle:
    def area(self):
        return math.pi * self.radius ** 2

    def to_svg(self):
        return f'<circle r="{self.radius}"/>'

    def to_dxf(self):
        return f"CIRCLE {self.radius}"

    def price(self, rates):
        return self.area() * rates["circle"]

    def validate(self, rules):
        return self.radius <= rules["max_radius"]


class Square:
    def area(self):
        return self.side ** 2

    def to_svg(self):
        return f'<rect width="{self.side}" height="{self.side}"/>'

    def to_dxf(self):
        return f"POLYLINE {self.side}"

    def price(self, rates):
        return self.area() * rates["square"]
    # validate: never written, so validation silently passes every square
```

## Why it's bad

- The shapes are a stable set; the operations are not. Every new thing anyone wants to do with a shape — a
  second export format, billing, validation — is an edit to every shape class, by whoever owns that feature.
- One concern is spread over N classes and no class holds a concern. Reviewing "how do we price shapes" means
  reading five files and hoping to find them all; the DXF exporter's escaping rules live wherever a shape
  happens to be defined.
- Missing implementations are silent. `Square` has no `validate`, so validation either raises deep in a loop or,
  worse, is called behind a `hasattr` and passes. That is the presentation: a rule that turned out to apply to
  only some shapes, discovered from production data.
- The model class ends up importing the billing rates, the SVG conventions and the validation rules, so the
  geometry cannot be used without all of them.
- This is the opposite pressure to `isinstance-chain-instead-of-dispatch`, and the two entries mark the two
  choices: put behaviour on the class when the types keep arriving, and use a visitor when the types are settled
  and the operations keep arriving. Both are wrong applied to the other case.

## Better

```python
class Circle:
    def accept(self, visitor):
        return visitor.circle(self)

    def area(self):
        return math.pi * self.radius ** 2


class Square:
    def accept(self, visitor):
        return visitor.square(self)

    def area(self):
        return self.side ** 2


class SvgExport:
    """One operation, in one place, complete for every shape."""

    def circle(self, shape):
        return f'<circle r="{shape.radius}"/>'

    def square(self, shape):
        return f'<rect width="{shape.side}" height="{shape.side}"/>'


class Pricing:
    def __init__(self, rates):
        self._rates = rates

    def circle(self, shape):
        return shape.area() * self._rates["circle"]

    def square(self, shape):
        return shape.area() * self._rates["square"]


def render(shapes):
    return "".join(shape.accept(SvgExport()) for shape in shapes)
```

The shapes keep only geometry, each concern is one readable class, and a shape the visitor forgot is an
`AttributeError` at the point of use rather than a rule that quietly did not apply.
