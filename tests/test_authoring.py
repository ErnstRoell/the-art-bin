"""Tests for the two authoring entry points: new_smell.py and install.sh.

Both are one-command conveniences whose value is entirely in not having to check the
result by hand, so what is tested here is the guarantee each one makes: a scaffolded file
passes the validator untouched, and an installed config points a client at this checkout.

`validate.py` and `new_smell.py` live at the repository root rather than in the package,
so they are imported by path.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


validate = _load("validate")
new_smell = _load("new_smell")


@pytest.fixture
def scaffold(tmp_path, monkeypatch):
    """Scaffold into a throwaway tree, so the real corpus and catalog stay untouched."""
    group_dir = tmp_path / "snippets" / "python" / "code"
    group_dir.mkdir(parents=True)
    monkeypatch.setattr(new_smell, "SNIPPETS", tmp_path / "snippets")
    monkeypatch.setattr(new_smell, "ROOT", tmp_path)
    monkeypatch.setattr(validate, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["new_smell.py"])
    return group_dir


def run_new_smell(*args: str) -> None:
    monkeyargv = ["new_smell.py", *args]
    sys.argv[:] = monkeyargv
    assert new_smell.main() == 0


def test_scaffolded_file_passes_the_validator(scaffold) -> None:
    """The placeholders are deliberately schema-valid: a fresh file fails nothing but staleness."""
    run_new_smell("brand-new-smell", "--severity", "taste", "--category", "readability", "--topic", "naming")

    errors = validate.Errors()
    record = validate.check_file(
        scaffold / "brand-new-smell.md", validate.load_taxonomy(), errors
    )
    assert errors.items == []
    assert record is not None
    assert record["entry"]["id"] == "brand-new-smell"
    assert record["entry"]["severity"] == "taste"
    assert record["entry"]["category"] == "readability"
    assert record["entry"]["topic"] == "naming"


def test_scaffold_keeps_the_template_body(scaffold) -> None:
    run_new_smell("another-smell", "--severity", "bug", "--category", "correctness", "--topic", "io")
    text = (scaffold / "another-smell.md").read_text(encoding="utf-8")

    assert "# Another smell" in text
    assert "## Smell" in text and "## Why it's bad" in text and "## Better" in text
    # Untouched template fields, including the two that need thought.
    assert 'signature: "One sentence naming the mechanism' in text
    assert "distinguish:" in text
    assert "aliases: []" in text


def test_title_and_source_are_overridable(scaffold) -> None:
    run_new_smell(
        "third-smell",
        "--severity",
        "bug",
        "--category",
        "security",
        "--topic",
        "io",
        "--title",
        "A better title",
        "--source",
        "someone",
    )
    text = (scaffold / "third-smell.md").read_text(encoding="utf-8")
    assert "# A better title" in text
    assert "source: someone" in text


def test_empty_source_drops_the_optional_field(scaffold) -> None:
    run_new_smell(
        "fourth-smell", "--severity", "bug", "--category", "security", "--topic", "io", "--source", ""
    )
    assert "source:" not in (scaffold / "fourth-smell.md").read_text(encoding="utf-8")


def test_slug_must_be_a_slug(scaffold) -> None:
    with pytest.raises(SystemExit) as exit_info:
        run_new_smell("Not A Slug", "--severity", "bug", "--category", "correctness", "--topic", "io")
    assert "[a-z0-9-]+" in str(exit_info.value)


def test_existing_id_is_refused(scaffold) -> None:
    run_new_smell("taken", "--severity", "bug", "--category", "correctness", "--topic", "io")
    with pytest.raises(SystemExit) as exit_info:
        run_new_smell("taken", "--severity", "bug", "--category", "correctness", "--topic", "io")
    assert "already the id or an alias" in str(exit_info.value)


def test_existing_alias_is_refused(scaffold) -> None:
    (scaffold / "aliased.md").write_text(
        "---\naliases: [also-known-as]\nlanguage: python\n---\n\n# X\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exit_info:
        run_new_smell("also-known-as", "--severity", "bug", "--category", "correctness", "--topic", "io")
    assert "already the id or an alias" in str(exit_info.value)


def test_taxonomy_values_come_from_the_taxonomy_file(scaffold) -> None:
    with pytest.raises(SystemExit) as exit_info:
        run_new_smell("bad-topic", "--severity", "bug", "--category", "correctness", "--topic", "vibes")
    assert "not one of" in str(exit_info.value)


def test_missing_field_without_a_terminal_lists_the_choices(scaffold) -> None:
    """Non-interactive callers get the closed list in the error, not a hanging prompt."""
    with pytest.raises(SystemExit) as exit_info:
        run_new_smell("no-topic", "--severity", "bug", "--category", "correctness")
    message = str(exit_info.value)
    assert "--topic is required" in message
    assert "mutability" in message


def test_neighbours_finds_smells_sharing_a_word() -> None:
    """The duplicate hint runs against the real corpus, which is the only place it is useful."""
    assert "mutable-default-argument" in new_smell.neighbours("mutable-default-list", limit=5)
    assert new_smell.neighbours("zzz-nothing-like-this") == []


def test_install_script_prints_a_config_for_this_checkout() -> None:
    result = subprocess.run(
        [str(ROOT / "install.sh"), "--client", "print"],
        capture_output=True,
        text=True,
        check=True,
    )
    config = json.loads(result.stdout)
    server = config["mcpServers"]["the-art-bin"]
    assert server["command"] == "uv"
    assert server["args"] == ["--directory", str(ROOT), "run", "art-bin-server"]


def test_install_script_merges_into_an_existing_config(tmp_path) -> None:
    config_path = tmp_path / "mcp.json"
    config_path.write_text(
        json.dumps({"mcpServers": {"other": {"command": "node"}}, "theme": "dark"}), encoding="utf-8"
    )
    subprocess.run(
        [str(ROOT / "install.sh"), "--config", str(config_path), "--name", "art-bin", "--no-check"],
        capture_output=True,
        text=True,
        check=True,
    )

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["theme"] == "dark", "unrelated keys must survive the patch"
    assert set(config["mcpServers"]) == {"other", "art-bin"}
    assert config["mcpServers"]["art-bin"]["args"][1] == str(ROOT)
    assert (tmp_path / "mcp.json.bak").exists(), "the previous config is backed up"


def test_install_script_refuses_to_clobber_without_force(tmp_path) -> None:
    config_path = tmp_path / "mcp.json"
    config_path.write_text(json.dumps({"mcpServers": {"the-art-bin": {"command": "stale"}}}), encoding="utf-8")
    command = [str(ROOT / "install.sh"), "--config", str(config_path), "--no-check"]

    refused = subprocess.run(command, capture_output=True, text=True)
    assert refused.returncode == 1
    assert "--force" in refused.stdout + refused.stderr
    assert json.loads(config_path.read_text(encoding="utf-8"))["mcpServers"]["the-art-bin"]["command"] == "stale"

    subprocess.run([*command, "--force"], capture_output=True, text=True, check=True)
    assert json.loads(config_path.read_text(encoding="utf-8"))["mcpServers"]["the-art-bin"]["command"] == "uv"


def test_install_dry_run_changes_nothing(tmp_path) -> None:
    config_path = tmp_path / "mcp.json"
    result = subprocess.run(
        [str(ROOT / "install.sh"), "--config", str(config_path), "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["mcpServers"]["the-art-bin"]["command"] == "uv"
    assert not config_path.exists()
