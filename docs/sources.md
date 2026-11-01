---
title: Sources
description: How every smell in the corpus is tied to the published passage that states its claims, and how those links were checked.
status: draft
created: 2026-09-30
updated: 2026-09-30
author: jeremy
tags: [corpus, sources]
category: reference
related:
  - docs/python-sources.md
  - docs/rust-sources.md
  - docs/typescript-sources.md
  - docs/adr/014-every-claim-traced-to-a-source.md
---

# Sources

Every entry in the corpus is tied, claim by claim, to a published source:

- [Python](./python-sources.md)
- [Rust](./rust-sources.md)
- [TypeScript](./typescript-sources.md)

## What a row says

A row names one entry, one claim it makes, a link, and a quote. The claim is either part of the mechanism in
`## Why it's bad` or the fix in `## Better`. The link goes to **the place in the source that states the claim**,
not to the page's top. It uses the section's own anchor (`...#why-is-this-bad`, `...#method.unwrap`) when one
lands close enough, and a text fragment (`...#:~:text=...`) when none does. Browsers that support text fragments
scroll to the sentence and highlight it. The Passage column quotes the source verbatim, at most 30 words, so a
reader can judge the claim without clicking.

An entry usually has several rows: one per claim a reader might doubt, and two independent sources where they
exist, typically official documentation plus a respected book, style guide or blog.

`house taste` in the Source column marks a style preference of the corpus that no source states. `severity:
taste` exists for exactly those entries, and the corpus does not invent support for them.

Each page ends with a **Not sourced** section. It lists claims that were left without a row because they are
arithmetic on the entry's own example, a measurement, or the entry's own argument. It also lists the entries
that were corrected when a source disagreed with them.

## How the rows were checked

Every row was checked twice, against the raw page rather than a summary of it.

1. While writing it, the author downloaded the page and confirmed the anchor or fragment text and the quote
   appeared in it.
2. Afterwards, an independent pass re-downloaded every linked page and checked each of the three things again:
   - a `#id` anchor exists in the HTML (GitHub's `user-content-` prefix allowed);
   - a text fragment's text appears in the page's text;
   - the quote appears verbatim, ignoring markup and whitespace.

   All 952 rows passed.

Some sources needed a different link:

- **Pages that render in the browser**, where the text is not in the downloaded HTML: the row links the same
  statement in a server-rendered page or in the project's source repository, and says so.
- **PyTorch:** the `stable` docs URL is a JavaScript redirect that drops the fragment, so those links are
  pinned to the 2.14 docs.
- **Books** are cited through the text their authors publish: *Effective TypeScript*'s "Things to Remember"
  in its repository, and *You Don't Know JS* on GitHub.

Links rot. A row whose anchor or quote no longer matches its page is a row to fix, not to delete. The claim was
true of the source when it was written, and the fix is usually a newer anchor on the same page.

## The reference shelf

Official documentation carries most rows:

- **Python:** the Python docs, PEP 8, Ruff and Pylint rules, NumPy, pandas and PyTorch.
- **Rust:** std, the Book, the Reference, Clippy, the API Guidelines, Tokio and crate docs on docs.rs.
- **TypeScript:** MDN, the TypeScript handbook and release notes, typescript-eslint and ESLint rules, Node.js,
  React and OWASP.
- **Architecture:** refactoring.guru for the patterns in all three languages.

Beyond those:

- Dan Vanderkam, *Effective TypeScript*, 2nd ed. (O'Reilly, 2024): https://github.com/danvk/effective-typescript
- David Drysdale, *Effective Rust*: https://effective-rust.com/
- *Rust Design Patterns*: https://rust-unofficial.github.io/patterns/
- The Rust API Guidelines: https://rust-lang.github.io/api-guidelines/
- Kyle Simpson, *You Don't Know JS*, 1st ed.: https://github.com/getify/You-Dont-Know-JS
- Google's Python and TypeScript style guides: https://google.github.io/styleguide/
- *The Hitchhiker's Guide to Python*: https://docs.python-guide.org/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- Martin Fowler's bliki: https://martinfowler.com/bliki/
- patterns.dev, Addy Osmani and Lydia Hallie: https://www.patterns.dev/
- Jake Archibald, "await vs return vs return await":
  https://jakearchibald.com/2017/await-vs-return-vs-return-await/
