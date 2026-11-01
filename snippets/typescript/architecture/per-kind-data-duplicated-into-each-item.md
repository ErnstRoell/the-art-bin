---
aliases: []
language: typescript
typescript: ">=3.4"
severity: trap
category: performance
topic: classes
tags: [flyweight, memory, sharing, immutability]
keywords: ["structuredClone(", "{ ...kind", "new Path2D(", "loadSprite(", "Array.from({ length", "for (let i = 0; i < count"]
signature: "Every object in a large collection gets its own copy or freshly loaded instance of state that is identical across them, so memory and setup cost scale with the number of objects rather than the number of distinct values."
distinguish: "Fine when the duplicated state is small, or when each object really does modify its own copy independently."
added: 2026-09-30
source: refactoring.guru
---

# Per-kind data duplicated into each item

## Smell

```typescript
interface ParticleKind {
  name: string;
  sprite: ImageBitmap;       // decoded pixels
  palette: string[];
  mass: number;
}

interface Particle {
  x: number;
  y: number;
  kind: ParticleKind;
  outline: Path2D;
}

export function spawnBurst(kind: ParticleKind, count: number): Particle[] {
  return Array.from({ length: count }, () => ({
    x: Math.random() * WIDTH,
    y: Math.random() * HEIGHT,
    kind: { ...kind, palette: [...kind.palette] },   // defensive copy per particle
    outline: new Path2D(SPARK_SVG_PATH),             // same path, parsed again every time
  }));
}

export async function spawnRain(count: number): Promise<Particle[]> {
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    const sprite = await loadSprite("/sprites/drop.png");   // fetched and decoded per drop
    particles.push({ x: i * 4, y: 0, kind: { name: "drop", sprite, palette: BLUES, mass: 1 }, outline: DROP });
  }
  return particles;
}
```

## Why it's bad

- A particle's own state is its position; the sprite, palette, mass and outline belong to its kind. Storing
  them per particle makes memory proportional to particles times kind size instead of the number of kinds.
- `spawnRain` decodes the same image once per drop, so a heavy shower is a frame-time spike and a pile of
  identical bitmaps, and nothing at the call site says an image load is happening.
- The spread copies exist because nothing says the kind is shared, so a defensive copy was cheaper to write
  than the reasoning, and changing a kind's palette now means walking every particle.

## Better

```typescript
const kinds = new Map<string, Promise<Readonly<ParticleKind>>>();

function kind(name: string, spritePath: string, palette: readonly string[], mass: number) {
  if (!kinds.has(name)) {
    kinds.set(name, loadSprite(spritePath).then((sprite) => ({ name, sprite, palette: [...palette], mass })));
  }
  return kinds.get(name)!;
}

interface Particle {
  x: number;
  y: number;
  readonly kind: Readonly<ParticleKind>;   // shared by reference, never copied
}

export async function spawnRain(count: number): Promise<Particle[]> {
  const drop = await kind("drop", "/sprites/drop.png", BLUES, 1);
  return Array.from({ length: count }, (_, i) => ({ x: i * 4, y: 0, kind: drop }));
}
```

In JavaScript an object reference is already shared, so the flyweight is mostly a matter of not copying:
each kind is loaded once, typed `Readonly` so nobody feels the need to clone it, and every particle points at
it.
