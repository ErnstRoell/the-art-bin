"""End-to-end tests over a real stdio subprocess.

Each test opens its own client: an async-generator fixture would enter and exit the
transport's cancel scope in different tasks, which anyio rejects.
"""

import json
import sys
from typing import Any

from mcp import Client, StdioServerParameters

PARAMS = StdioServerParameters(command=sys.executable, args=["-m", "art_bin_server"])


def connect() -> Client:
    return Client(PARAMS, raise_exceptions=True)


def payload(result: Any) -> Any:
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    return json.loads(result.content[0].text)


async def test_tools_are_advertised_read_only() -> None:
    async with connect() as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        assert set(tools) == {"list_smells", "get_smells", "get_taxonomy"}
        for tool in tools.values():
            assert tool.annotations.read_only_hint is True
            assert tool.description


async def test_instructions_state_the_two_phase_contract() -> None:
    async with connect() as client:
        assert "distinguish" in client.instructions
        assert "Do not guess smell ids" in client.instructions


async def test_no_tool_accepts_source_code() -> None:
    """docs/003: nothing in this API takes code as input."""
    async with connect() as client:
        for tool in (await client.list_tools()).tools:
            properties = tool.input_schema.get("properties", {})
            assert not {"code", "source", "path", "file", "snippet"} & set(properties)


async def test_list_then_get_round_trip() -> None:
    async with connect() as client:
        catalog = payload(await client.call_tool("list_smells", {}))
        assert catalog["count"] == 10
        assert "distinguish" not in catalog["smells"][0]

        shortlist = [catalog["smells"][0]["id"], catalog["smells"][1]["id"]]
        records = payload(await client.call_tool("get_smells", {"ids": shortlist}))
        assert [record["id"] for record in records["smells"]] == shortlist
        assert all(record["distinguish"] for record in records["smells"])
        assert all(record["better"] for record in records["smells"])
        assert records["unknown"] == []


async def test_filters_and_taxonomy_agree() -> None:
    async with connect() as client:
        taxonomy = payload(await client.call_tool("get_taxonomy", {}))
        for severity, count in taxonomy["severity"].items():
            result = payload(await client.call_tool("list_smells", {"severity": [severity]}))
            assert result["count"] == count


async def test_alias_resolves_over_the_wire() -> None:
    async with connect() as client:
        result = payload(await client.call_tool("get_smells", {"ids": ["swallowed-exception"]}))
        record = result["smells"][0]
        assert record["id"] == "bare-except-pass"
        assert record["resolved_from"] == "swallowed-exception"


async def test_hallucinated_id_does_not_fail_the_call() -> None:
    async with connect() as client:
        result = payload(
            await client.call_tool("get_smells", {"ids": ["bare-except-pass", "not-a-real-smell"]})
        )
        assert len(result["smells"]) == 1
        assert result["unknown"] == ["not-a-real-smell"]
