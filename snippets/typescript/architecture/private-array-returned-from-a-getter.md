---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [iterator, encapsulation, aliasing, generators]
keywords: ["return this.tracks;", "getTracks(): Track[]", "private tracks: Track[]", ".push(...", ".splice(i, 1)", "*[Symbol.iterator]()"]
signature: "A class returns the private array it stores so callers can loop over it, so any caller can mutate the object's internals through the value it was given."
distinguish: "Fine when the getter returns a fresh copy the caller is meant to own, or the class keeps no invariant over the array so exposing it hides nothing."
added: 2026-09-30
source: refactoring.guru
---

# Private array returned from a getter

## Smell

```typescript
export class Playlist {
  private tracks: Track[] = [];
  private seconds = 0;

  add(track: Track): void {
    this.tracks.push(track);
    this.seconds += track.seconds;
  }

  getTracks(): Track[] {
    return this.tracks;               // the caller now holds the playlist's own array
  }

  get duration(): number {
    return this.seconds;
  }
}

export function merged(a: Playlist, b: Playlist): Track[] {
  const tracks = a.getTracks();
  tracks.push(...b.getTracks());      // edits `a`, and its duration is now wrong
  return tracks.sort(byTitle);        // and reorders it in place as well
}

export function dropExplicit(playlist: Playlist): void {
  const tracks = playlist.getTracks();
  tracks.forEach((track, i) => {
    if (track.explicit) tracks.splice(i, 1);   // splicing mid-loop skips the next track
  });
}
```

## Why it's bad

- `private` only hides the property name. The getter hands out the array itself, so every caller has write
  access to the state the keyword was meant to protect.
- The class's invariant is unenforceable. `add` keeps `seconds` in step with `tracks`; `merged` pushes behind
  its back, so the object is inconsistent without any method having been called wrongly.
- Functions whose names promise no side effects have them. `merged(a, b)` silently edits and sorts `a`, since
  `Array.prototype.sort` works in place.
- `dropExplicit` splices the array it is looping over and skips elements, a mistake made easy by handing the
  array out at all.
- The return type locks in the representation. `tracks` can never become a linked list, a query or a lazy
  stream, because every caller was promised a mutable array.

## Better

```typescript
export class Playlist implements Iterable<Track> {
  private readonly tracks: Track[] = [];
  private seconds = 0;

  add(track: Track): void {
    this.tracks.push(track);
    this.seconds += track.seconds;
  }

  remove(track: Track): void {
    const i = this.tracks.indexOf(track);
    if (i < 0) return;
    this.tracks.splice(i, 1);
    this.seconds -= track.seconds;
  }

  /** Iteration without a handle: callers can loop, not reach in. */
  *[Symbol.iterator](): IterableIterator<Track> {
    yield* this.tracks.slice();
  }

  get duration(): number {
    return this.seconds;
  }
}

export const merged = (a: Playlist, b: Playlist): Track[] => [...a, ...b].sort(byTitle);

export function dropExplicit(playlist: Playlist): void {
  for (const track of playlist) if (track.explicit) playlist.remove(track);
}
```

`for...of` and spread are the whole interface, mutation goes through methods that keep `duration` true, and the
generator iterates a snapshot, so removing during a loop is safe rather than subtly wrong.
