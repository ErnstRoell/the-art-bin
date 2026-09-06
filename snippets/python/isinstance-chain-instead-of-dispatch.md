---
aliases: [type-switch, isinstance-ladder]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [polymorphism, dispatch, open-closed]
keywords: ["isinstance(", "elif isinstance", "raise TypeError", "if isinstance(shape"]
signature: "A chain of isinstance branches switches on the type of an object the module owns, so adding a type means editing this function."
distinguish: "Fine at a boundary that must handle types it does not own, such as a serialiser for third-party objects."
added: 2026-09-04
source: ernst
---

# Isinstance chain instead of dispatch

## Smell

```python
def area(shape):
    if isinstance(shape, Circle):
        return math.pi * shape.radius ** 2
    if isinstance(shape, Square):
        return shape.side ** 2
    if isinstance(shape, Rectangle):
        return shape.width * shape.height
    raise TypeError(shape)
```

## Why it's bad

- The knowledge of how to measure a circle lives away from `Circle`, so understanding that class requires
  finding every function that switches on it.
- Adding `Triangle` means editing this function, and every other function shaped like it, and the compiler
  cannot tell you where they are — the `raise TypeError` only fires at runtime, for whichever shape was hit
  first.
- The chain grows monotonically, is order-sensitive once any of these types subclass another, and the fallback
  branch is dead code that nonetheless has to be maintained.
- It presents as a bug report about one shape type, fixed in one of the four places that needed it.

## Better

```python
class Circle:
    def area(self):
        return math.pi * self.radius ** 2


class Square:
    def area(self):
        return self.side ** 2


def area(shape):
    return shape.area()
```
