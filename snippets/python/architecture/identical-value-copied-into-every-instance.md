---
aliases: [missing-flyweight, intrinsic-state-duplicated-per-object]
language: python
python: ">=3.0"
severity: trap
category: performance
topic: classes
tags: [flyweight, memory, sharing, immutability]
keywords: ["for _ in range(", "load_sprite", "list(", "copy(", "def __init__(self, x, y", "[Particle("]
signature: "Every object in a large collection carries its own copy of state that is identical across them, so memory and setup cost scale with the number of objects rather than the number of distinct values."
distinguish: "Fine when the duplicated state is small, or when each object really does mutate its own copy."
added: 2026-09-06
source: refactoring.guru
---

# Identical value copied into every instance

## Smell

```python
class Particle:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.sprite = load_sprite(kind)        # decoded again, per particle
        self.palette = list(PALETTES[kind])    # copied so it is "safe" to mutate
        self.mass = KINDS[kind]["mass"]

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y), self.palette)

    def step(self, dt):
        self.y += self.mass * dt


def burst(kind, count):
    return [Particle(random(), random(), kind) for _ in range(count)]


smoke = burst("smoke", 50_000)      # 50_000 decodes of one image, 50_000 palettes
```

## Why it's bad

- Two particles of the same kind differ only in position. Everything else — sprite, palette, mass — is a
  property of the *kind*, stored per particle, so the memory cost is the number of particles times the size of
  a sprite instead of the number of kinds.
- `load_sprite` runs once per object. The cost is invisible at the call site, which reads as a list
  comprehension, and shows up as a frame-time spike whenever a burst spawns rather than as a slow function.
- Nobody mutates `palette`, but the copy exists because nothing says it is shared, so the defensive copy is
  cheaper to write than the reasoning. That is how this grows: each field is individually only a few kilobytes.
- It presents as a memory ceiling nobody can attribute. The heap is full of duplicate immutable data, so
  profiles blame the object count and the fix looks like "spawn fewer particles".

## Better

```python
@dataclass(frozen=True)
class ParticleKind:
    """Intrinsic state: shared, immutable, one instance per distinct kind."""

    sprite: object
    palette: tuple
    mass: float


@lru_cache(maxsize=None)
def kind(name):
    spec = KINDS[name]
    return ParticleKind(load_sprite(name), tuple(PALETTES[name]), spec["mass"])


class Particle:
    """Extrinsic state only: what actually differs between particles."""

    __slots__ = ("x", "y", "kind")

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.kind = kind(name)

    def draw(self, screen):
        screen.blit(self.kind.sprite, (self.x, self.y), self.kind.palette)

    def step(self, dt):
        self.y += self.kind.mass * dt


def burst(name, count):
    return [Particle(random(), random(), name) for _ in range(count)]
```

One sprite per kind, decoded once, and the shared state is frozen so sharing it is safe by construction rather
than by everyone remembering not to write to it.
