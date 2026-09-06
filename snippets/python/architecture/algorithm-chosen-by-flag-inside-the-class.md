---
aliases: [missing-strategy, mode-retested-in-every-method]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [strategy, dispatch, modes, open-closed]
keywords: ["self.mode ==", "if self.kind ==", "self.mode", "elif self.mode", "def __init__(self, mode", "mode="]
signature: "One mode flag is re-tested in every method of a class, so a single algorithm is smeared across the class instead of living in one object."
distinguish: "Fine when only one method varies with the flag, where a lookup table at that one site is the simpler fix."
added: 2026-09-06
source: refactoring.guru
---

# Algorithm chosen by flag inside the class

## Smell

```python
class Route:
    def __init__(self, mode):
        self.mode = mode

    def duration(self, a, b):
        if self.mode == "car":
            return road_distance(a, b) / 50
        if self.mode == "walk":
            return road_distance(a, b) / 5
        return great_circle(a, b) / 800

    def waypoints(self, a, b):
        if self.mode == "car":
            return road_path(a, b)
        if self.mode == "walk":
            return foot_path(a, b)
        return [a, b]

    def emissions(self, a, b):
        if self.mode == "car":
            return road_distance(a, b) * 120
        return 0            # walking and flying, apparently the same


class Itinerary:
    def cost(self, route, a, b):
        if route.mode == "car":     # the flag has escaped the class
            return road_distance(a, b) * FUEL
        return TICKET[route.mode]
```

## Why it's bad

- Everything that makes a car a car is spread over four methods in two classes. Adding cycling means finding
  every test of `mode` — including the one in `Itinerary` that nobody remembers — and the compiler cannot tell
  you where they are.
- The branches drift out of alignment. `emissions` has two cases where the others have three, so flying is
  attributed zero emissions by omission rather than by decision, and nothing in the code marks it as a stub.
- Each method's fallback is `else`, so a typo in `mode` is not an error; it is a flight. There is no list of
  valid modes anywhere to check against.
- This is `equality-chain-instead-of-lookup-table` after it has spread. That entry is one chain producing one
  value, where the fix is a dict; here the same key is tested in several methods, which is what makes an object
  the fix rather than a table.

## Better

```python
class CarStrategy:
    def duration(self, a, b):
        return road_distance(a, b) / 50

    def waypoints(self, a, b):
        return road_path(a, b)

    def emissions(self, a, b):
        return road_distance(a, b) * 120

    def cost(self, a, b):
        return road_distance(a, b) * FUEL


class FlightStrategy:
    def duration(self, a, b):
        return great_circle(a, b) / 800

    def waypoints(self, a, b):
        return [a, b]

    def emissions(self, a, b):
        return great_circle(a, b) * 250

    def cost(self, a, b):
        return TICKET["flight"]


STRATEGIES = {"car": CarStrategy, "flight": FlightStrategy}


class Route:
    def __init__(self, mode):
        self._strategy = STRATEGIES[mode]()

    def duration(self, a, b):
        return self._strategy.duration(a, b)

    def emissions(self, a, b):
        return self._strategy.emissions(a, b)
```

One mode is one class, so a new mode is a new file rather than four edits, an unknown mode raises at
construction, and a missing method is an `AttributeError` instead of a silent zero.
