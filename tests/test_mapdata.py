# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for loading, validating, and inverting the map data."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scripts import mapdata

MINIMAL = textwrap.dedent(
    """
    programme:
      title: "T"
      question: "Q"
      move: "M"
    strands:
      adequacy:
        title: "A"
        subtitle: "a"
    stages:
      define: "d"
    repos:
      - key: alpha
        owner: systems-researcher
        strand: adequacy
        stage: define
        objective: "o"
        question: "q"
        method: "m"
        status: design
    """
)


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "repos.yml"
    path.write_text(text, encoding="utf-8")
    return path


def test_load_returns_blocks_and_indexes_repos_by_key(tmp_path: Path) -> None:
    data = mapdata.load(write(tmp_path, MINIMAL))

    assert data.programme["title"] == "T"
    assert data.stages["define"] == "d"
    assert list(data.by_key) == ["alpha"]
    assert data.by_key["alpha"]["render"] == "card"


def test_load_raises_with_line_and_column_on_syntax_error(tmp_path: Path) -> None:
    with pytest.raises(mapdata.MapError) as excinfo:
        mapdata.load(write(tmp_path, "programme:\n  title: 'unterminated\n"))

    assert "line" in str(excinfo.value)


def base() -> dict:
    """A minimal valid data structure, as dicts, for rule-level tests."""
    return {
        "programme": {"title": "T", "question": "Q", "move": "M"},
        "strands": {"adequacy": {"title": "A", "subtitle": "a"}},
        "stages": {"define": "d"},
        "repos": [
            {
                "key": "alpha",
                "owner": "systems-researcher",
                "strand": "adequacy",
                "stage": "define",
                "render": "card",
                "objective": "o",
                "question": "q",
                "method": "m",
                "status": "design",
                "depends_on": [],
            }
        ],
    }


def check(raw: dict) -> list[str]:
    data = mapdata.MapData(
        programme=raw["programme"],
        strands=raw["strands"],
        stages=raw["stages"],
        repos=raw["repos"],
    )
    data.by_key = {entry["key"]: entry for entry in raw["repos"] if "key" in entry}
    return mapdata.check(data)


def errors_of(raw: dict) -> list[str]:
    return check(raw)


def test_valid_data_produces_no_errors() -> None:
    assert check(base()) == []


def test_rule_1_depends_on_names_a_key_that_does_not_exist() -> None:
    raw = base()
    raw["repos"][0]["depends_on"] = ["ghost"]

    errors = check(raw)

    assert any("alpha" in e and "ghost" in e for e in errors)


def test_rule_2_stage_outside_the_permitted_set() -> None:
    """The stages block gains 'prototype' so rule 8 cannot fire and mask rule 2."""
    raw = base()
    raw["stages"]["prototype"] = "p"
    raw["repos"][0]["stage"] = "prototype"

    assert any("not one of" in e and "prototype" in e for e in errors_of(raw))


def test_rule_3_missing_required_field_including_on_node_only() -> None:
    raw = base()
    raw["repos"][0]["render"] = "node-only"
    del raw["repos"][0]["method"]

    assert any("method" in e for e in errors_of(raw))


def test_rule_4_terminus_may_not_be_depended_on() -> None:
    raw = base()
    raw["repos"].append(
        {
            "key": mapdata.TERMINUS,
            "owner": "systems-researcher",
            "strand": "adequacy",
            "stage": "define",
            "render": "node-only",
            "objective": "o",
            "question": "q",
            "method": "m",
            "status": "not-applicable",
            "depends_on": [],
        }
    )
    raw["repos"][0]["depends_on"] = [mapdata.TERMINUS]

    assert any(mapdata.TERMINUS in e and "alpha" in e for e in errors_of(raw))


def test_rule_5_headline_requires_a_result_status() -> None:
    raw = base()
    raw["repos"][0]["headline"] = {"text": "42%", "source": "somewhere v1"}

    assert any("headline" in e and "design" in e for e in errors_of(raw))


def test_rule_5_not_applicable_only_on_node_only_entries() -> None:
    raw = base()
    raw["repos"][0]["status"] = "not-applicable"

    assert any("not-applicable" in e for e in errors_of(raw))


def test_rule_5_node_only_is_reserved_for_the_terminus() -> None:
    """Without this, node-only plus not-applicable would hide any study entirely."""
    raw = base()
    raw["repos"][0]["render"] = "node-only"
    raw["repos"][0]["status"] = "not-applicable"

    assert any("node-only" in e and mapdata.TERMINUS in e for e in errors_of(raw))


def test_rule_6_headline_needs_both_text_and_source() -> None:
    raw = base()
    raw["repos"][0]["status"] = "published"
    raw["repos"][0]["headline"] = {"text": "42% of answers"}

    assert any("source" in e for e in errors_of(raw))


def test_rule_7_duplicate_key() -> None:
    raw = base()
    raw["repos"].append(dict(raw["repos"][0]))

    assert any("duplicate" in e.lower() and "alpha" in e for e in errors_of(raw))


def test_rule_7_owner_must_look_like_an_account_name() -> None:
    raw = base()
    raw["repos"][0]["owner"] = "not a name!"

    assert any("owner" in e for e in errors_of(raw))


def test_rule_8_stage_used_with_no_explanation_line() -> None:
    raw = base()
    raw["repos"][0]["stage"] = "measure"

    assert any("stages" in e and "measure" in e for e in errors_of(raw))


def test_rule_8_programme_block_is_required() -> None:
    raw = base()
    del raw["programme"]["move"]

    assert any("programme.move" in e for e in errors_of(raw))


def test_rule_9_self_reference_is_a_cycle() -> None:
    raw = base()
    raw["repos"][0]["depends_on"] = ["alpha"]

    assert any("cycle" in e.lower() and "alpha" in e for e in errors_of(raw))


def test_rule_9_reports_the_full_cycle_path() -> None:
    raw = base()
    raw["repos"][0]["depends_on"] = ["beta"]
    raw["repos"].append(
        {
            "key": "beta",
            "owner": "systems-researcher",
            "strand": "adequacy",
            "stage": "define",
            "render": "card",
            "objective": "o",
            "question": "q",
            "method": "m",
            "status": "design",
            "depends_on": ["alpha"],
        }
    )

    message = " ".join(errors_of(raw))

    assert "alpha" in message and "beta" in message and "cycle" in message.lower()


def test_feeds_is_the_inverse_of_depends_on() -> None:
    raw = base()
    raw["repos"].append(
        {
            "key": "beta",
            "owner": "systems-researcher",
            "strand": "adequacy",
            "stage": "define",
            "render": "card",
            "objective": "o",
            "question": "q",
            "method": "m",
            "status": "design",
            "depends_on": ["alpha"],
        }
    )
    data = mapdata.MapData(
        programme=raw["programme"],
        strands=raw["strands"],
        stages=raw["stages"],
        repos=raw["repos"],
    )
    data.by_key = {e["key"]: e for e in raw["repos"]}

    feeds = mapdata.feeds(data)

    assert feeds["alpha"] == ["beta"]
    assert feeds["beta"] == []


# --- Rule 10: paper citations -------------------------------------------------


def _with_paper(fields: dict[str, str]) -> str:
    """MINIMAL's single entry, plus a paper block built from `fields`.

    MINIMAL is dedented, so the entry's keys sit at four spaces
    ("    owner: ..."). The paper mapping joins them there, its members at six.
    """
    lines = ["    paper:"]
    lines += [f"      {name}: {value}" for name, value in fields.items()]
    return MINIMAL.rstrip("\n") + "\n" + "\n".join(lines) + "\n"


def test_a_complete_paper_citation_passes(tmp_path: Path) -> None:
    data = mapdata.load(
        write(
            tmp_path,
            _with_paper(
                {
                    "title": '"T"',
                    "venue": '"MODELS 2026 (NIER)"',
                    "year": "2026",
                    "doi": '"10.1145/3822455.3838783"',
                }
            ),
        )
    )

    assert mapdata.check(data) == []


@pytest.mark.parametrize("missing", ["title", "venue", "year", "doi"])
def test_a_half_filled_citation_is_rejected(tmp_path: Path, missing: str) -> None:
    """A venue on the page with nothing a reader can follow is worse than
    no citation at all."""
    fields = {
        "title": '"T"',
        "venue": '"MODELS 2026 (NIER)"',
        "year": "2026",
        "doi": '"10.1145/3822455.3838783"',
    }
    del fields[missing]
    data = mapdata.load(write(tmp_path, _with_paper(fields)))

    errors = mapdata.check(data)

    assert any(missing in error and "paper is missing" in error for error in errors)


def test_a_doi_written_as_a_url_is_rejected(tmp_path: Path) -> None:
    """The bare DOI is what a citation manager and a resolver both want."""
    data = mapdata.load(
        write(
            tmp_path,
            _with_paper(
                {
                    "title": '"T"',
                    "venue": '"V"',
                    "year": "2026",
                    "doi": '"https://doi.org/10.1145/3822455.3838783"',
                }
            ),
        )
    )

    errors = mapdata.check(data)

    assert any("does not start with" in error for error in errors)


def test_an_entry_without_a_paper_is_unaffected(tmp_path: Path) -> None:
    data = mapdata.load(write(tmp_path, MINIMAL))

    assert mapdata.check(data) == []
