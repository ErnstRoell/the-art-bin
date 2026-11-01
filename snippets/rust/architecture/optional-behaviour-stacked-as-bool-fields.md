---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: functions
tags: [decorator, composition, io, wrappers]
keywords: ["compress: bool", "encrypt: bool", "buffered: bool", "if self.compress {", "if opts.", "checksum: bool"]
signature: "A writer or service takes several bool options for independent optional behaviours, so its body interleaves all of them and the number of paths through it doubles with each flag."
distinguish: "Fine when the options are configuration values for one behaviour rather than separate behaviours layered on top of it."
added: 2026-09-23
source: refactoring.guru
---

# Optional behaviour stacked as bool fields

## Smell

```rust
pub struct ExportOptions {
    pub compress: bool,
    pub encrypt: bool,
    pub checksum: bool,
}

pub fn export(data: &[u8], out: &mut File, opts: &ExportOptions, key: &Key) -> io::Result<()> {
    let mut bytes = data.to_vec();
    if opts.compress {
        bytes = gzip(&bytes)?;
    }
    if opts.encrypt {
        bytes = encrypt(&bytes, key)?;
    }
    let digest = if opts.checksum { Some(sha256(&bytes)) } else { None };
    out.write_all(&bytes)?;
    if let Some(digest) = digest {
        out.write_all(&digest)?;
    }
    Ok(())
}
```

## Why it's bad

- Three flags are eight paths, and the order between them — compress before encrypt, checksum after both — is
  buried in the sequence of `if`s. Nobody can get a checksum of the plaintext without editing this function.
- Every layer materialises the whole payload in memory, because the flags force the steps into one function
  that works on a `Vec`, so a 4 GB export needs 12 GB.
- A fourth behaviour, such as rate limiting, is a new field, a new branch and a new test matrix.
- `key` is a required argument even when `encrypt` is false, which is what flag-shaped options always do to a
  signature.

## Better

```rust
pub fn export(data: &mut impl Read, mut out: impl Write) -> io::Result<()> {
    io::copy(data, &mut out)?;
    out.flush()
}

// Each behaviour is a Write that wraps another Write, stacked in the order the caller wants:
let file = File::create(path)?;
let sink = HashingWriter::new(file);                          // checksum of what hits the disk
let sink = EncryptingWriter::new(sink, &key);
let sink = flate2::write::GzEncoder::new(sink, Compression::default());
export(&mut source, sink)?;
```

Each behaviour is one type implementing `Write`, the same interface as the thing it wraps. They stream,
compose in any order, and `export` knows none of them exist.
