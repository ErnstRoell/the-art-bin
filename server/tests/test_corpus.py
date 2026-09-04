"""Unit tests for the reading layer."""

import pytest

from art_bin_server.corpus import Corpus, _bullets, _matches_version


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


def test_version_filter_excludes_smells_that_do_not_apply(corpus: Corpus) -> None:
    """naive-datetime-for-instants is >=3.2, since timezone landed in 3.2."""
    ids_31 = {smell["id"] for smell in corpus.list_smells(python_version="3.1")["smells"]}
    ids_312 = {smell["id"] for smell in corpus.list_smells(python_version="3.12")["smells"]}
    assert "naive-datetime-for-instants" not in ids_31
    assert "naive-datetime-for-instants" in ids_312


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
