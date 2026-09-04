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
| `snippets/python/` | The corpus. One smell per file. |
| `catalog.json` | Generated summary of every smell, small enough to read whole. |
| `TAXONOMY.md` | The closed lists a smell is filed against. |
| `TEMPLATE.md` | Skeleton for a new smell. |
| `validate.py` | Schema and constraint checks. Runs in CI. |
| `server/` | The MCP server. |
| `CONTEXT.md` | The project glossary. |
| `docs/` | Design documents and architecture decision records. |

## Using it

Register the MCP server with your client and ask it to review code:

```json
{
  "mcpServers": {
    "the-art-bin": {
      "command": "uv",
      "args": ["--directory", "/path/to/the-art-bin/server", "run", "art-bin-server"]
    }
  }
}
```

It exposes three read-only tools — `list_smells`, `get_smells`, `get_taxonomy` — and no analysis. The corpus
goes to the model; the model does the judging. See [server/README.md](./server/README.md).

## Adding a smell

```sh
cp TEMPLATE.md snippets/python/my-new-smell.md
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
