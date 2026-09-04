"""MCP tool surface over the corpus.

Three read-only tools and no analysis: nothing here accepts source code, scores anything,
or decides what matches. The calling model has the target code in context and does the
judging (docs/adr/001). The tool descriptions carry the usage contract, because the value
of the corpus depends on callers following it.
"""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from .corpus import Corpus, CorpusError

INSTRUCTIONS = """\
The Art Bin is a curated corpus of Python code smells — from outright bugs to matters of \
house taste. Use it to ground a code review in specific, named, opinionated entries \
instead of generic advice.

Work in two phases:

1. Call `list_smells` once and read the catalog against the code in front of you. Shortlist \
the few smells that might plausibly apply. Do not guess smell ids.
2. Call `get_smells` for that shortlist. Read each `distinguish` field before reporting \
anything — it describes the legitimate variant that merely resembles the smell, and it is \
the guard against flagging correct code.

Cite the smell `id` in every finding so a reader can go read the entry. Respect `severity`: \
`taste` is a house-style preference and should be reported as one, not as a bug.\
"""

READ_ONLY = ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False)


def build_server(corpus: Corpus | None = None) -> MCPServer:
    corpus = corpus or Corpus.discover()
    server = MCPServer(
        name="the-art-bin",
        title="The Art Bin",
        version="0.1.0",
        instructions=INSTRUCTIONS,
    )

    @server.tool(
        annotations=READ_ONLY,
        description=(
            "Return the catalog of known Python smells: one compact entry each, with a "
            "signature naming the mechanism, plus severity, category, topic, tags and "
            "keywords. Call this first, with no arguments, and read it against the code "
            "you are reviewing to shortlist candidates. Full snippets are deliberately "
            "not included here — fetch those with get_smells for the few that look "
            "plausible."
        ),
    )
    def list_smells(
        severity: Annotated[
            list[str] | None,
            Field(description="Restrict to any of: bug, trap, taste."),
        ] = None,
        category: Annotated[
            list[str] | None,
            Field(description="Restrict by consequence, e.g. correctness, security, readability."),
        ] = None,
        topic: Annotated[
            list[str] | None,
            Field(description="Restrict by Python feature, e.g. exceptions, mutability, naming."),
        ] = None,
        language: Annotated[str, Field(description="Corpus language.")] = "python",
        python_version: Annotated[
            str | None,
            Field(description="Only smells that apply to this Python version, e.g. '3.12'."),
        ] = None,
    ) -> dict[str, Any]:
        return corpus.list_smells(
            severity=severity,
            category=category,
            topic=topic,
            language=language,
            python_version=python_version,
        )

    @server.tool(
        annotations=READ_ONLY,
        description=(
            "Return full records for specific smells: the offending snippet, why it is "
            "bad, the corrected version, and the `distinguish` line describing the near "
            "miss that is NOT this smell. Read `distinguish` before reporting a finding. "
            "Accepts slugs or aliases; unrecognised ids come back in `unknown` rather "
            "than failing the call."
        ),
    )
    def get_smells(
        ids: Annotated[
            list[str],
            Field(description="Smell ids from list_smells. Aliases resolve transparently."),
        ],
    ) -> dict[str, Any]:
        return corpus.get_smells(ids)

    @server.tool(
        annotations=READ_ONLY,
        description=(
            "Return the closed lists a smell can be filed against — category, topic and "
            "severity — with the number of smells in each. Use it to build valid "
            "list_smells filters instead of guessing at values."
        ),
    )
    def get_taxonomy() -> dict[str, Any]:
        return corpus.taxonomy()

    return server


def main() -> int:
    try:
        server = build_server()
    except CorpusError as exc:
        print(f"art-bin-server: {exc}", flush=True)
        return 1
    server.run("stdio")
    return 0
