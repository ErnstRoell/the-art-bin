---
aliases: []
language: rust
rust: ">=1.26"
severity: trap
category: correctness
topic: mutability
tags: [iterator, encapsulation, invariants]
keywords: ["-> &mut Vec<", "-> &Vec<", "pub fn items(&mut self)", "pub fn items(&self)", "impl Iterator<Item ="]
signature: "A struct hands out its internal Vec so callers can loop over it, so every caller can reach the struct's invariants and every caller depends on the collection it happens to use."
distinguish: "Fine for a plain data struct with no invariants between its fields, or a function that returns a freshly built Vec the caller owns."
added: 2026-09-23
source: refactoring.guru
---

# Internal Vec handed out by mutable reference

## Smell

```rust
pub struct Playlist {
    tracks: Vec<Track>,
    total: Duration,       // must equal the sum of track lengths
}

impl Playlist {
    pub fn add(&mut self, track: Track) {
        self.total += track.length;
        self.tracks.push(track);
    }

    pub fn tracks(&mut self) -> &mut Vec<Track> {
        &mut self.tracks
    }

    pub fn total(&self) -> Duration {
        self.total
    }
}

// elsewhere, removing explicit tracks:
// playlist.tracks().retain(|t| !t.explicit);
// playlist.total() is now wrong
```

## Why it's bad

- `add` maintains `total`; `tracks()` hands callers a way around `add`. Any caller can push, remove or reorder
  and the playlist's duration is silently wrong afterwards.
- Returning `&Vec<Track>` instead avoids that, but still promises callers a `Vec`, so moving to a `VecDeque`
  or a tree breaks every call site that reached for `len` or indexing.
- The mistake presents far from here, as a duration display that disagrees with the tracks shown next to it.

## Better

```rust
impl Playlist {
    pub fn add(&mut self, track: Track) {
        self.total += track.length;
        self.tracks.push(track);
    }

    pub fn tracks(&self) -> impl Iterator<Item = &Track> + '_ {
        self.tracks.iter()
    }

    pub fn remove_where(&mut self, mut unwanted: impl FnMut(&Track) -> bool) {
        self.tracks.retain(|track| !unwanted(track));
        self.total = self.tracks.iter().map(|track| track.length).sum();
    }
}
```

Callers can iterate without knowing the collection, and every mutation goes through a method that keeps the
invariant.
