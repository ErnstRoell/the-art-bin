# The art bin

The place to share your special snowflakes, pet peeves and other works of art. 
All so your LLM can learn what not to do and for you to have a good laugh.

```python
this_is_true = False

if not this_is_true:
    print("You are such a special snowflake!")
```

## What this is

A corpus of bad Python code, one **smell** per file, structured so a machine can find the ones your codebase
resembles. An MCP server serves the corpus to an LLM reviewing real code, so instead of generic advice you get
"line 42 is `mutable-default-argument`, here is why, here is what to write instead."

Linters already own the mechanically detectable defects — `ruff` and Semgrep will find bare excepts forever.
What no linter ships is *taste*: the house style, the pet peeves, the patterns that run fine and that your team
still refuses to accept. That knowledge normally lives in reviewers' heads and leaks out one PR comment at a
time. This makes it addressable.

## Layout

| Path | What it is |
| --- | --- |
| `snippets/python/code/` | The corpus. One smell per file, 15 lines or fewer. |
| `snippets/python/architecture/` | Smells that live between components, where 15 lines cannot show the problem. One entry per Gang of Four pattern, describing the code the pattern answers. |
| `catalog.json` | Generated summary of every smell, small enough to read whole. |
| `TAXONOMY.md` | The closed lists a smell is filed against. |
| `TEMPLATE.md` | Skeleton for a new smell. |
| `validate.py` | Schema and constraint checks. Runs in CI. |
| `src/art_bin_server/` | The MCP server. |
| `tests/` | Tests for the server, run against the real corpus. |
| `CONTEXT.md` | The project glossary. |
| `docs/` | Design documents and architecture decision records. |

## Using it

Register the MCP server with your client and ask it to review code:

```json
{
  "mcpServers": {
    "the-art-bin": {
      "command": "uv",
      "args": ["--directory", "/path/to/the-art-bin", "run", "art-bin-server"]
    }
  }
}
```

It exposes three read-only tools and no analysis — nothing here accepts source code, scores anything, or
decides what matches. The corpus goes to the model; the model does the judging
([ADR 001](./docs/adr/001-corpus-as-queryable-knowledge-base.md)).

| Tool | Returns |
| --- | --- |
| `list_smells` | The whole catalog: id, signature, severity, category, topic, tags, keywords. Optional filters for severity, category, topic, language and `python_version`. |
| `get_smells` | Full records for specific ids: snippet, why it's bad, corrected version, and `distinguish`. Aliases resolve; unknown ids come back in `unknown`. |
| `get_taxonomy` | The closed lists with corpus counts, for building valid filters. |

Callers are expected to work in two phases — one `list_smells` to shortlist, one `get_smells` to confirm. The
server's `instructions` field states that contract, and the full surface is specified in
[MCP API Overview](./docs/003-mcp-api-overview.md).

The server finds the corpus by walking up from its own location until it finds a directory containing both
`catalog.json` and `snippets/`. Set `ART_BIN_ROOT` to point somewhere else — which is what a deployment that
separates the server from the corpus would do.

## Developing the server

```sh
uv sync
uv run pytest -q          # 27 tests, including 7 over a real stdio subprocess
uv run art-bin-server     # start on stdio
```

`src/art_bin_server/corpus.py` is the reading layer — catalog, record parsing, alias resolution, filters — and
`src/art_bin_server/server.py` is the tool surface. Frontmatter parsing is deliberately duplicated between
`corpus.py` and `validate.py`, so that contributors can validate a snippet without installing the server. The
schema they agree on is [Snippet Design](./docs/002-snippet-design.md).

## Adding a smell

```sh
cp TEMPLATE.md snippets/python/code/my-new-smell.md
# write it
uv run validate.py --write-catalog
```

Read [CONTRIBUTING.md](./CONTRIBUTING.md) first — particularly the part about never pasting code from a real
codebase, and the three fields that need actual thought.

## Design

- [System Overview](./docs/001-system-overview.md) — the three parts, and why this is not a vector search
- [Snippet Design](./docs/002-snippet-design.md) — the file format, field by field
- [MCP API Overview](./docs/003-mcp-api-overview.md) — the tool surface
- [Decision records](./docs/adr/) — ten ADRs covering the decisions behind all of it

## Licensing and disclaimer

The corpus under `snippets/` is [CC0](./snippets/LICENSE) — public domain, no attribution required, ingest it
however you like. The tooling is [MIT](./LICENSE).

Every snippet here is a **minimal reconstruction** written to illustrate a smell. Nothing in this repository is
an excerpt of any real codebase, none of it is intended to be run, and all of it is provided without warranty
of any kind. The opinions are opinions — `severity: taste` means exactly that.
