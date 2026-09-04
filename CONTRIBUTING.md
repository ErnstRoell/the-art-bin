# Contributing

One smell per file. Small, self-contained, and written from scratch.

## Before you start

**Never paste code from a real codebase.** Every snippet here is a *reconstruction*: a minimal example written
from scratch to illustrate a smell. This is not a formality. Pasting from work republishes someone else's
unlicensed code, and a recognisable snippet publishes a colleague's work as an example of what not to do. The
15-line ceiling exists partly to make this easy — no real code is that small, so rebuilding is the only way to
hit it.

Check whether the smell is already here. Search `catalog.json` for the mechanism before writing a new file.

## Adding a smell

1. Copy `TEMPLATE.md` to `snippets/python/<slug>.md`.
2. Name the slug after the smell, not the fix: `mutable-default-argument`, not `use-none-default`.
3. Fill in the frontmatter. Every field except `aliases` and `source` is required.
4. Write the three body sections: `## Smell`, `## Why it's bad`, `## Better`.
5. Regenerate the catalog: `uv run validate.py --write-catalog`.
6. Commit both your snippet and the updated `catalog.json`.

## The fields that need thought

Most of the frontmatter is filing. Three fields are the actual work.

**`signature`** — one sentence naming the *mechanism*. This is what an LLM reads when deciding whether your
smell is worth investigating, so write it to be matched, not to be read aloud. "A function default is a list or
dict, so one object is shared across every call" is a signature. "Causes confusing bugs" is not.

**`distinguish`** — one sentence describing the *near miss*: code that looks like your smell but is fine. This
is the most valuable field in the corpus, because the main failure mode of the whole system is flagging correct
code that merely resembles a smell. If you cannot write the near miss, you do not yet understand your smell
well enough to add it.

**`keywords`** — literal tokens and phrases that appear in or near the offending code: `"=[]"`, `"except:"`,
`"time.sleep"`. Lexical hooks, not concepts. A keyword that never appears in real code is useless. Concepts go
in `tags`.

## Severity

Be honest about what the smell costs. The corpus is useless if a naming preference is filed with the same weight
as a SQL injection.

- `bug` — wrong today; produces incorrect behaviour as written
- `trap` — works today, bites later; correct until a condition changes
- `taste` — works and keeps working, but reads badly

`taste` is welcome and is most of the point of this project. It carries one extra obligation: `## Better` has to
be good, because "I dislike this" is unactionable without "write this instead".

## Rules the validator enforces

Run `uv run validate.py` before opening a pull request. CI runs the same thing, and everything hard-blocks.

- The `## Smell` block is 15 lines or fewer
- Both code blocks parse under `ast.parse` — they need not run, and `...` is fine
- `category` and `topic` are values listed in `TAXONOMY.md`
- `signature` and `distinguish` are each a single sentence ending in a period
- The filename matches `[a-z0-9-]+`, and no alias collides with any other slug or alias
- The three H2 sections are present, in order
- `catalog.json` matches what regeneration would produce

Adding a `category` or `topic` value means editing `TAXONOMY.md` in the same pull request, and that is a
deliberate change — check that nothing existing fits first.

## Out of scope for now

Smells that need more than 15 lines to demonstrate, and architecture-level anti-patterns. They do not fit this
schema and should not be squeezed into it. They are a later project.

## Attribution

`source` is optional credit for whoever contributed the smell. It is not a provenance field for the code —
there is no provenance, because the snippet is a reconstruction.

Contributions to `snippets/` are released under [CC0](./snippets/LICENSE).
