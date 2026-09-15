"""MCP server for The Art Bin corpus of Python code smells."""

from .corpus import Corpus, CorpusError, parse_record
from .server import build_server, main

__all__ = ["Corpus", "CorpusError", "parse_record", "build_server", "main"]
