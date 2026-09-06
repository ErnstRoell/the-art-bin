# The Art Bin

A curated corpus of bad Python code, one specimen per file, structured so a machine
can find the ones a real codebase resembles.

## Language

**Smell**:
A single named way that code goes wrong, and the unit of this corpus — one smell per
file. Ranges from outright defects to matters of taste.
_Avoid_: Anti-pattern, pet peeve, snowflake, violation

**Severity**:
How much a smell actually costs: `bug` (wrong today), `trap` (works today, bites
later), or `taste` (works and keeps working, but reads badly).
_Avoid_: Priority, importance, level

**Category**:
What a smell costs you — its consequence, e.g. correctness or readability. One value
per smell, from a closed list.
_Avoid_: Kind, type, class

**Topic**:
What a smell is made of — the Python feature it lives in, e.g. exceptions or
mutability. One value per smell, from a closed list.
_Avoid_: Area, subject, domain

**Tags**:
Open-ended labels on a smell, for anything Category and Topic don't capture.

**Keywords**:
Literal tokens and phrases likely to appear in code that has a given smell. Lexical
hooks for finding candidates, as opposed to [[Tags]], which are conceptual.
_Avoid_: Terms, search terms, triggers

**Signature**:
The one sentence naming a smell's mechanism, written to be matched against unfamiliar
code rather than read aloud.
_Avoid_: Summary, description, headline

**Distinguish**:
The one sentence describing the near miss — code that resembles a smell but is
legitimate.
_Avoid_: Exception, false positive, caveat, when it's OK

**Better**:
The corrected version of a smell's snippet — what to write instead.
_Avoid_: Fix, good version, solution, remedy

**Group**:
The directory a smell is filed under below its language — `code` or `architecture`. It
selects the snippet size ceiling and carries no other meaning.
_Avoid_: Kind, tier, section, folder

**Catalog**:
The compact summary of every smell in the corpus, small enough to be read whole.
Holds signatures and labels, never snippets.
_Avoid_: Index, manifest, database

**Reconstruction**:
A snippet rebuilt from scratch to illustrate a smell, rather than copied from a real
codebase. Every snippet in the corpus is one.
_Avoid_: Example, sample, excerpt
