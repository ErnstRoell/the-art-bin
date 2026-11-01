---
aliases: []
language: rust
rust: ">=1.0"
severity: bug
category: security
topic: io
tags: [unsafe, deserialisation, undefined-behaviour, parsing]
keywords: ["ptr::read(", "read_unaligned(", "transmute", "as *const Header", "from_raw_parts(", "unsafe {"]
signature: "Bytes read from a file or socket are reinterpreted as a struct with unsafe pointer casts or transmute, so input the program did not produce can hold values the type forbids."
distinguish: "Fine when the target type is plain data in which every bit pattern is valid, the cast is checked by a crate such as bytemuck or zerocopy, and length and alignment are verified first."
added: 2026-09-23
source: jeremy-wayland
---

# Untrusted bytes cast into a struct

## Smell

```rust
#[repr(C)]
pub struct Header {
    pub kind: Kind,          // enum with three variants
    pub compressed: bool,
    pub len: u32,
}

pub fn parse_header(bytes: &[u8]) -> Header {
    unsafe { std::ptr::read(bytes.as_ptr() as *const Header) }
}
```

## Why it's bad

- A `bool` that is not 0 or 1, or an enum discriminant outside its variants, is undefined behaviour the
  moment it exists. A crafted file hands the optimiser a value it assumes impossible, and what happens next is
  not bounded by anything in the source.
- `ptr::read` also requires alignment, which a `&[u8]` does not provide, and nothing checks that `bytes` is
  long enough, so a short file reads past the buffer.
- It is the Rust version of loading a pickle: the input decides what the program's memory means. Unlike
  pickle, it passes every test built from well-formed files.

## Better

```rust
pub fn parse_header(bytes: &[u8]) -> Result<Header, HeaderError> {
    let [kind, compressed, _, _, len @ ..] = *bytes.first_chunk::<8>().ok_or(HeaderError::Truncated)?;
    Ok(Header {
        kind: Kind::try_from(kind)?,
        compressed: match compressed {
            0 => false,
            1 => true,
            other => return Err(HeaderError::BadFlag(other)),
        },
        len: u32::from_le_bytes(len),
    })
}
```
