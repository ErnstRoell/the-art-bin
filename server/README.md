# art-bin-server

MCP server exposing [The Art Bin](../README.md) corpus of Python code smells over stdio.

Three read-only tools and no analysis. Nothing here accepts source code, scores anything, or decides what
matches — the calling model has the target code in context and does the judging
([ADR 001](../docs/adr/001-corpus-as-queryable-knowledge-base.md)).

## Install

```sh
cd server
uv sync
```

## Register with an MCP client

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

The server finds the corpus by walking up from its own location until it finds a directory containing both
`catalog.json` and `snippets/`. Set `ART_BIN_ROOT` to point somewhere else — which is what a deployment that
separates the server from the corpus would do.

## Tools

| Tool | Returns |
| --- | --- |
| `list_smells` | The whole catalog: id, signature, severity, category, topic, tags, keywords. Optional filters for severity, category, topic, language and `python_version`. |
| `get_smells` | Full records for specific ids: snippet, why it's bad, corrected version, and `distinguish`. Aliases resolve; unknown ids come back in `unknown`. |
| `get_taxonomy` | The closed lists with corpus counts, for building valid filters. |

Callers are expected to work in two phases — one `list_smells` to shortlist, one `get_smells` to confirm. The
server's `instructions` field states that contract, and the full surface is specified in
[MCP API Overview](../docs/003-mcp-api-overview.md).

## Layout

| Path | What it is |
| --- | --- |
| `src/art_bin_server/corpus.py` | Reading layer: catalog, record parsing, alias resolution, filters |
| `src/art_bin_server/server.py` | Tool surface and the usage contract in `instructions` |
| `tests/test_corpus.py` | Unit tests over the real corpus |
| `tests/test_server_e2e.py` | End-to-end tests against the server as a stdio subprocess |

Frontmatter parsing is deliberately duplicated between `corpus.py` and the repository's `validate.py`, so that
contributors can validate a snippet without installing this server. The schema they agree on is
[Snippet Design](../docs/002-snippet-design.md).

## Develop

```sh
uv run pytest -q          # 27 tests, including 7 over a real stdio subprocess
uv run art-bin-server     # start on stdio
```
