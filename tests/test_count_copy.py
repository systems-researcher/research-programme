# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Source pin for visitor count copy.

The page used to type its study totals. These asserts reject the frozen
word and the old templates. They do not execute the components and they
do not assert a derived integer: that integer belongs to data/map.json,
which this package does not own.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "src"
GRAPH = APP / "components" / "graph.tsx"
PUBLICATIONS = APP / "components" / "publications.tsx"
MATRIX = APP / "components" / "matrix.tsx"
PAGE = APP / "App.tsx"


def test_graph_source_has_no_frozen_twelve() -> None:
    assert "twelve" not in GRAPH.read_text(encoding="utf-8")


def test_publications_source_has_no_frozen_twelve() -> None:
    assert "twelve" not in PUBLICATIONS.read_text(encoding="utf-8")


def test_hero_label_is_studies_not_repositories() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert 'label: "Studies"' in text
    assert 'label: "Repositories"' not in text


def test_matrix_source_has_no_written_up() -> None:
    assert "written up" not in MATRIX.read_text(encoding="utf-8")


def test_publications_blurb_names_a_paper() -> None:
    text = PUBLICATIONS.read_text(encoding="utf-8")
    assert "have a paper" in text or "has a paper" in text
    assert "entered the record" not in text
