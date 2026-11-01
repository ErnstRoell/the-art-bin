---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: io
tags: [paths, filesystem, portability, utf-8]
keywords: ['format!("{}/{}"', '.display(), ', 'push_str("/', '+ "/" +', "-> String", ".to_str().unwrap()"]
signature: "A filesystem path is assembled with format or string concatenation, so separators are written by hand and the path is forced through UTF-8 text."
distinguish: "Fine for URL paths, object-store keys and other identifiers that are always slash-separated text rather than filesystem paths."
added: 2026-09-23
source: jeremy-wayland
---

# Path assembled via format

## Smell

```rust
pub fn thumbnail_path(cache_dir: &Path, image: &Path) -> String {
    let stem = image.file_stem().unwrap().to_str().unwrap();
    format!("{}/thumbs/{}.png", cache_dir.display(), stem)
}
```

## Why it's bad

- `display()` is lossy: any non-UTF-8 byte in the cache directory becomes U+FFFD, and the resulting string
  names a directory that does not exist. `to_str().unwrap()` panics on the same input in the file name.
- A `cache_dir` given with a trailing slash produces `//thumbs`, and a Windows path produces a mixture of
  separators that some tools accept and others do not.
- Returning `String` throws away the `Path` type, so every caller converts back and the next function repeats
  the same string surgery.

## Better

```rust
pub fn thumbnail_path(cache_dir: &Path, image: &Path) -> Option<PathBuf> {
    let stem = image.file_stem()?;
    Some(cache_dir.join("thumbs").join(stem).with_extension("png"))
}
```
