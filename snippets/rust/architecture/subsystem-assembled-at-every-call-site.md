---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: classes
tags: [facade, encapsulation, setup, teardown]
keywords: ["Decoder::new(", "Resampler::new(", "Encoder::new(", ".flush()?;", ".finish()?;", "let mut decoder ="]
signature: "A caller builds several collaborators of a subsystem it does not own and sequences their setup, ordering and teardown itself, so the same wiring is retyped at every call site."
distinguish: "Fine when the caller genuinely needs the fine-grained control, such as a tool that tunes each stage, and the subsystem also offers the simple path."
added: 2026-09-23
source: refactoring.guru
---

# Subsystem assembled at every call site

## Smell

```rust
pub fn make_preview(input: &Path, output: &Path) -> Result<(), MediaError> {
    let file = File::open(input)?;
    let mut demuxer = Demuxer::new(BufReader::new(file))?;
    let stream = demuxer.best_audio_stream().ok_or(MediaError::NoAudio)?;
    let mut decoder = Decoder::for_codec(stream.codec(), stream.params())?;
    let mut resampler = Resampler::new(stream.sample_rate(), 22_050, stream.channels(), 1)?;
    let mut encoder = Encoder::mp3(22_050, 1, Bitrate::Kbps(64))?;
    let mut out = BufWriter::new(File::create(output)?);

    while let Some(packet) = demuxer.next_packet(stream.index())? {
        for frame in decoder.decode(&packet)? {
            let resampled = resampler.process(&frame)?;
            out.write_all(&encoder.encode(&resampled)?)?;
        }
    }
    for frame in decoder.flush()? {
        out.write_all(&encoder.encode(&resampler.process(&frame)?)?)?;
    }
    out.write_all(&resampler.flush().and_then(|tail| encoder.encode(&tail))?)?;
    out.write_all(&encoder.finish()?)?;
    out.flush()?;
    Ok(())
}

// make_waveform, make_ringtone and transcode_upload repeat most of this
```

## Why it's bad

- Six collaborators, their construction parameters and a three-stage flush order are copied into every caller.
  The flush order is the kind of detail each copy gets slightly wrong, which shows up as audio clipped at the
  end.
- Callers depend on every type in the media subsystem, so replacing the resampler touches every feature that
  produces audio.
- The actual intent — "a 64 kbps mono MP3 preview of this file" — is not visible at the call site.

## Better

```rust
pub struct AudioConverter {
    sample_rate: u32,
    channels: u16,
    bitrate: Bitrate,
}

impl AudioConverter {
    pub fn mp3_preview() -> Self {
        Self { sample_rate: 22_050, channels: 1, bitrate: Bitrate::Kbps(64) }
    }

    /// Owns the pipeline: demux, decode, resample, encode, and the flush order between them.
    pub fn convert(&self, input: &Path, output: &Path) -> Result<(), MediaError> {
        // the pipeline above, written once
    }
}

pub fn make_preview(input: &Path, output: &Path) -> Result<(), MediaError> {
    AudioConverter::mp3_preview().convert(input, output)
}
```

The subsystem's types stay available for the rare caller that needs them, and everyone else calls one method
that says what it wants.
