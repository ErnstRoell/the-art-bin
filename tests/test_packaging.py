"""Tests for installing the server as a standalone tool.

The corpus lives at the repo root, outside the package, so nothing about `packages =
["src/art_bin_server"]` ships it. These tests cover the two halves that make
`uv tool install` work: the wheel carries a copy of the corpus, and `find_root` falls
back to that copy when there is no checkout above the module.
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from art_bin_server.corpus import CorpusError, _bundled_root, find_root

REPO_ROOT = Path(__file__).resolve().parents[1]


def make_bundle(base: Path) -> Path:
    """Build the layout the wheel ships: a _corpus/ dir holding catalog.json and snippets/."""
    bundle = base / "_corpus"
    (bundle / "snippets" / "python" / "code").mkdir(parents=True)
    (bundle / "catalog.json").write_text('{"schema_version": 1, "smells": []}', encoding="utf-8")
    return bundle


def test_a_checkout_ships_no_bundle() -> None:
    """Running from a clone, the corpus is the checkout itself and no bundle exists."""
    assert _bundled_root() is None


def test_bundle_is_found_beside_the_module(tmp_path: Path) -> None:
    bundle = make_bundle(tmp_path)
    assert _bundled_root(tmp_path) == bundle


def test_incomplete_bundle_is_not_a_root(tmp_path: Path) -> None:
    """catalog.json without snippets/ is a broken build, not a corpus to serve from."""
    bundle = make_bundle(tmp_path)
    shutil.rmtree(bundle / "snippets")
    assert _bundled_root(tmp_path) is None


def test_checkout_wins_over_the_bundle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A contributor running from a clone reads their own edits, not a stale bundled copy."""
    monkeypatch.delenv("ART_BIN_ROOT", raising=False)
    monkeypatch.setattr("art_bin_server.corpus._bundled_root", lambda base=None: tmp_path)
    assert find_root() == REPO_ROOT


def test_bundle_is_used_when_no_checkout_is_above_the_module(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The installed-tool case: the module sits in a venv with no corpus anywhere above it."""
    monkeypatch.delenv("ART_BIN_ROOT", raising=False)
    bundle = make_bundle(tmp_path)
    monkeypatch.setattr("art_bin_server.corpus._bundled_root", lambda base=None: bundle)
    assert find_root(start=tmp_path / "site-packages" / "art_bin_server" / "corpus.py") == bundle


def test_no_checkout_and_no_bundle_names_the_escape_hatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("ART_BIN_ROOT", raising=False)
    monkeypatch.setattr("art_bin_server.corpus._bundled_root", lambda base=None: None)
    with pytest.raises(CorpusError, match="ART_BIN_ROOT"):
        find_root(start=tmp_path / "nowhere" / "corpus.py")


def test_art_bin_root_overrides_both(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bundle = make_bundle(tmp_path)
    monkeypatch.setattr("art_bin_server.corpus._bundled_root", lambda base=None: bundle)
    monkeypatch.setenv("ART_BIN_ROOT", str(tmp_path / "_corpus"))
    assert find_root() == bundle


def test_art_bin_root_without_snippets_is_rejected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ART_BIN_ROOT", str(tmp_path))
    with pytest.raises(CorpusError, match="snippets/ directory"):
        find_root()


@pytest.mark.skipif(shutil.which("uv") is None, reason="needs uv to build a wheel")
@pytest.mark.skipif(
    not (REPO_ROOT / "pyproject.toml").is_file(), reason="needs a checkout to build from"
)
def test_wheel_bundles_the_corpus(tmp_path: Path) -> None:
    """Without this, `uv tool install` yields a server that cannot find its own corpus."""
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    (wheel,) = tmp_path.glob("*.whl")
    names = zipfile.ZipFile(wheel).namelist()

    assert "art_bin_server/_corpus/catalog.json" in names
    bundled = {n for n in names if n.startswith("art_bin_server/_corpus/snippets/")}
    on_disk = {
        f"art_bin_server/_corpus/snippets/{p.relative_to(REPO_ROOT / 'snippets')}"
        for p in (REPO_ROOT / "snippets").glob("*/*/*.md")
    }
    assert on_disk and on_disk <= bundled


@pytest.mark.skipif(shutil.which("uv") is None, reason="needs uv to build a wheel")
@pytest.mark.skipif(
    not (REPO_ROOT / "pyproject.toml").is_file(), reason="needs a checkout to build from"
)
def test_installed_tool_serves_the_corpus_without_a_checkout(tmp_path: Path) -> None:
    """The whole point: an install elsewhere on the filesystem still answers queries."""
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    (wheel,) = tmp_path.glob("*.whl")
    venv = tmp_path / "venv"
    subprocess.run(["uv", "venv", str(venv)], check=True, capture_output=True)
    python = venv / "bin" / "python"
    subprocess.run(
        ["uv", "pip", "install", "--python", str(python), str(wheel)],
        check=True,
        capture_output=True,
    )

    # cwd=/ and a cleared ART_BIN_ROOT leave the bundle as the only way to find the corpus.
    probe = (
        "from art_bin_server.corpus import Corpus, find_root;"
        "c = Corpus.discover();"
        "print(find_root().name, c.list_smells()['count'])"
    )
    result = subprocess.run(
        [str(python), "-c", probe],
        cwd=tmp_path.anchor,
        check=True,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    name, count = result.stdout.split()
    assert name == "_corpus"
    assert int(count) == len(list((REPO_ROOT / "snippets").glob("*/*/*.md")))


def test_console_script_entry_point_is_importable() -> None:
    """pyproject points art-bin-server at __main__:main; keep that target real."""
    module = __import__("art_bin_server.__main__", fromlist=["main"])
    assert callable(module.main)
