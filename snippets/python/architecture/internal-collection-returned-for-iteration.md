---
aliases: [missing-iterator, internals-handed-out-for-looping]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [iterator, encapsulation, aliasing, protocols]
keywords: ["return self._items", "return self._tracks", "def items(self)", ".extend(", "for x in obj.items()", "self._"]
signature: "A class hands out the list it stores so callers can loop over it, so any caller can reach the object's internals through the value it was given."
distinguish: "Fine when the returned collection is immutable or a fresh copy the caller is meant to own."
added: 2026-09-06
source: refactoring.guru
---

# Internal collection returned for iteration

## Smell

```python
class Playlist:
    def __init__(self):
        self._tracks = []

    def add(self, track):
        self._tracks.append(track)
        self._duration += track.length

    def tracks(self):
        return self._tracks        # the caller now holds the playlist's own list


def merge_into(playlist, other):
    tracks = playlist.tracks()
    tracks.extend(other.tracks())  # mutates playlist, and `_duration` is now a lie
    random.shuffle(tracks)
    return tracks


def first_ten(playlist):
    for track in playlist.tracks():
        if track.explicit:
            playlist.tracks().remove(track)   # mutating while iterating the same list
```

## Why it's bad

- `tracks()` reads as a getter and behaves as a handle on private state. The underscore on `_tracks` documents
  an intention the method then gives away.
- The class's invariants are unenforceable. `add` maintains `_duration`; `merge_into` appends behind its back,
  so the object is left internally inconsistent with no method having been called incorrectly.
- Callers get side effects from functions whose names promise none. `merge_into(a, b)` silently edits `a`,
  which is `argument-mutated-in-place` reached through a getter rather than a parameter.
- `first_ten` removes from the list it is iterating and skips elements, the classic
  `list-mutated-while-iterating` failure — made easy to write because the collection was handed out at all.
- The return type also locks the implementation in. `_tracks` can never become a deque, a query, or a lazy
  stream, because every caller has been promised a list.

## Better

```python
class Playlist:
    def __init__(self):
        self._tracks = []
        self._duration = 0

    def add(self, track):
        self._tracks.append(track)
        self._duration += track.length

    def remove(self, track):
        self._tracks.remove(track)
        self._duration -= track.length

    def __iter__(self):
        """Iteration without a handle: callers can loop, not reach in."""
        return iter(tuple(self._tracks))

    def __len__(self):
        return len(self._tracks)


def merged(playlist, other):
    tracks = [*playlist, *other]
    random.shuffle(tracks)
    return tracks


def drop_explicit(playlist):
    for track in playlist:
        if track.explicit:
            playlist.remove(track)
```

`for track in playlist` is now the whole interface, mutation goes through methods that keep `_duration` true,
and iterating over a snapshot makes removal during a loop safe instead of subtly wrong.
