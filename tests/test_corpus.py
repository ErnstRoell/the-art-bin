"""Unit tests for the reading layer."""

import pytest

from art_bin_server.corpus import Corpus, _bullets, _matches_version, parse_sources


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return Corpus.discover()


def test_catalog_matches_snippet_count(corpus: Corpus) -> None:
    catalog = corpus.catalog()
    assert catalog["count"] == len(catalog["smells"]) == len(corpus._snippet_paths())


def test_catalog_omits_confirm_phase_fields(corpus: Corpus) -> None:
    """distinguish and the snippets belong to get_smells, not the catalog (docs/adr/006)."""
    for smell in corpus.catalog()["smells"]:
        assert set(smell) == {
            "id",
            "signature",
            "severity",
            "category",
            "topic",
            "tags",
            "keywords",
            "language",
        }


def test_record_is_complete(corpus: Corpus) -> None:
    record = corpus.record("mutable-default-argument")
    assert record is not None
    assert record["title"] == "Mutable default argument"
    assert record["snippet"].startswith("def add_item(item, basket=[]):")
    assert "basket=None" in record["better"]
    assert record["distinguish"].endswith(".")
    assert len(record["why_bad"]) == 3


def test_every_smell_parses_and_has_a_better(corpus: Corpus) -> None:
    ids = [smell["id"] for smell in corpus.catalog()["smells"]]
    result = corpus.get_smells(ids)
    assert result["unknown"] == []
    assert len(result["smells"]) == len(ids)
    for record in result["smells"]:
        assert record["snippet"], record["id"]
        assert record["better"], record["id"]
        assert record["why_bad"], record["id"]
        assert record["distinguish"], record["id"]


def test_every_smell_carries_its_sources(corpus: Corpus) -> None:
    """docs/<language>-sources.md covers every entry (docs/adr/014)."""
    ids = [smell["id"] for smell in corpus.catalog()["smells"]]
    for record in corpus.get_smells(ids)["smells"]:
        assert record["sources"], record["id"]
        for row in record["sources"]:
            assert row["claim"] and row["passage"], record["id"]
            assert row["url"] is None or row["url"].startswith("https://"), row["url"]


def test_sources_rows_parse_links_escaped_pipes_and_plain_sources() -> None:
    rows = parse_sources(
        "| Smell | Claim | Source | Passage |\n|---|---|---|---|\n"
        '| [a-b](../snippets/x/code/a-b.md) | c | [T: s](https://e.x/p#:~:text=q) | "x \\|\\| y" |\n'
        "| [a-b](../snippets/x/code/a-b.md) | fix | house taste | no external source |\n"
    )
    first, second = rows["a-b"]
    assert first == {"claim": "c", "source": "T: s", "url": "https://e.x/p#:~:text=q", "passage": '"x || y"'}
    assert second["source"] == "house taste" and second["url"] is None


def test_alias_resolves_and_reports_origin(corpus: Corpus) -> None:
    result = corpus.get_smells(["mutable-default-arg"])
    record = result["smells"][0]
    assert record["id"] == "mutable-default-argument"
    assert record["resolved_from"] == "mutable-default-arg"


def test_unknown_ids_are_reported_not_raised(corpus: Corpus) -> None:
    result = corpus.get_smells(["bare-except-pass", "invented-by-a-model"])
    assert [record["id"] for record in result["smells"]] == ["bare-except-pass"]
    assert result["unknown"] == ["invented-by-a-model"]


def test_duplicate_requests_collapse(corpus: Corpus) -> None:
    result = corpus.get_smells(["wildcard-import", "star-import", "wildcard-import"])
    assert len(result["smells"]) == 1


@pytest.mark.parametrize("hostile", ["../../etc/passwd", "snippets/python/x", "Bad_Slug", ""])
def test_ids_are_not_treated_as_paths(corpus: Corpus, hostile: str) -> None:
    assert corpus.record(hostile) is None
    assert corpus.get_smells([hostile])["unknown"] == [hostile]


def test_filters_narrow_the_catalog(corpus: Corpus) -> None:
    """Counts are derived from the catalog, not hardcoded, so the corpus can grow."""
    smells = corpus.catalog()["smells"]
    taste = {smell["id"] for smell in smells if smell["severity"] == "taste"}
    security = {smell["id"] for smell in smells if smell["category"] == "security"}

    assert 0 < len(taste) < len(smells)
    assert 0 < len(security) < len(smells)
    assert corpus.list_smells(severity=["taste"])["count"] == len(taste)
    assert corpus.list_smells(category=["security"])["count"] == len(security)
    assert corpus.list_smells(severity=["taste"], category=["security"])["count"] == len(
        taste & security
    )
    assert corpus.list_smells(language="ruby")["count"] == 0
    assert corpus.list_smells(language="rust")["count"] > 0
    assert corpus.list_smells(language="python")["count"] > 0
    assert corpus.list_smells(language="typescript")["count"] > 0
    assert sum(corpus.list_smells(language=lang)["count"] for lang in ("python", "rust", "typescript")) == len(
        smells
    )


def test_version_filter_excludes_smells_that_do_not_apply(corpus: Corpus) -> None:
    """naive-datetime-for-instants is >=3.2, since timezone landed in 3.2."""
    ids_31 = {smell["id"] for smell in corpus.list_smells(python_version="3.1")["smells"]}
    ids_312 = {smell["id"] for smell in corpus.list_smells(python_version="3.12")["smells"]}
    assert "naive-datetime-for-instants" not in ids_31
    assert "naive-datetime-for-instants" in ids_312


def test_rust_version_filter_uses_the_rust_range(corpus: Corpus) -> None:
    """trim-matches-used-to-remove-one-suffix is >=1.45, since strip_suffix landed in 1.45."""
    old = corpus.list_smells(rust_version="1.44")["smells"]
    new = corpus.list_smells(rust_version="1.80")["smells"]
    assert "trim-matches-used-to-remove-one-suffix" not in {smell["id"] for smell in old}
    assert "trim-matches-used-to-remove-one-suffix" in {smell["id"] for smell in new}
    assert {smell["language"] for smell in new} == {"rust"}


def test_typescript_version_filter_uses_the_typescript_range(corpus: Corpus) -> None:
    """satisfies-operator-avoided-with-an-annotation is >=4.9, since satisfies landed in 4.9."""
    old = corpus.list_smells(typescript_version="4.8")["smells"]
    new = corpus.list_smells(typescript_version="5.4")["smells"]
    assert "satisfies-operator-avoided-with-an-annotation" not in {smell["id"] for smell in old}
    assert "satisfies-operator-avoided-with-an-annotation" in {smell["id"] for smell in new}
    assert {smell["language"] for smell in new} == {"typescript"}


def test_both_version_filters_keep_both_languages(corpus: Corpus) -> None:
    both = corpus.list_smells(python_version="3.12", rust_version="1.80")["count"]
    python = corpus.list_smells(python_version="3.12")["count"]
    rust = corpus.list_smells(rust_version="1.80")["count"]
    assert both == python + rust > 0


def test_taxonomy_counts_sum_to_the_corpus(corpus: Corpus) -> None:
    taxonomy = corpus.taxonomy()
    total = corpus.catalog()["count"]
    for field in ("category", "topic", "severity"):
        assert sum(taxonomy[field].values()) == total
    assert set(taxonomy["severity"]) <= {"bug", "trap", "taste"}


def test_bullets_fold_wrapped_lines() -> None:
    section = "- first bullet\n  wrapped onto a second line\n- second bullet\n"
    assert _bullets(section) == ["first bullet wrapped onto a second line", "second bullet"]


@pytest.mark.parametrize(
    ("spec", "version", "expected"),
    [
        (">=3.0", "3.13", True),
        (">=3.2", "3.1", False),
        ("<3.12", "3.13", False),
        (None, "3.13", True),
        ("nonsense", "3.13", True),
    ],
)
def test_version_matching(spec: str | None, version: str, expected: bool) -> None:
    assert _matches_version(spec, version) is expected
