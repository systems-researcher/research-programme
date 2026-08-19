# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for rendering the README block and the site page."""
from __future__ import annotations

from scripts import mapdata, render

BEGIN = "<!-- BEGIN:repos -->"
END = "<!-- END:repos -->"


def data_with(*entries: dict) -> mapdata.MapData:
    data = mapdata.MapData(
        programme={"title": "T", "question": "Q", "move": "M"},
        strands={
            "adequacy": {"title": "Adequacy", "subtitle": "sub"},
            "assembly": {"title": "Assembly", "subtitle": "sub"},
        },
        stages={"define": "d", "evidence": "e", "assembly": "a"},
        repos=list(entries),
    )
    data.by_key = {entry["key"]: entry for entry in entries}
    return data


def entry(**overrides: object) -> dict:
    base = {
        "key": "alpha",
        "owner": "systems-researcher",
        "strand": "adequacy",
        "stage": "define",
        "render": "card",
        "objective": "What alpha is for.",
        "question": "What does alpha answer?",
        "method": "How alpha answers it.",
        "status": "design",
        "depends_on": [],
    }
    base.update(overrides)
    return base


def test_readme_block_replaces_only_between_the_markers() -> None:
    original = f"# Title\n\nintro\n\n{BEGIN}\nstale\n{END}\n\noutro\n"

    updated = render.readme_block(original, data_with(entry()))

    assert updated.startswith("# Title\n\nintro\n")
    assert updated.endswith("outro\n")
    assert "stale" not in updated
    assert "alpha" in updated


def test_readme_block_raises_when_markers_are_absent() -> None:
    try:
        render.readme_block("# Title\nno markers\n", data_with(entry()))
    except render.RenderError as exc:
        assert "BEGIN:repos" in str(exc)
    else:
        raise AssertionError("expected RenderError")


def test_readme_table_lists_stage_status_and_objective() -> None:
    updated = render.readme_block(
        f"{BEGIN}\n{END}\n", data_with(entry(status="published"))
    )

    assert "| `alpha` |" in updated
    assert "define" in updated
    assert "published" in updated
    assert "What alpha is for." in updated


def test_mermaid_edges_run_from_dependency_to_consumer() -> None:
    data = data_with(
        entry(),
        entry(key="beta", stage="evidence", depends_on=["alpha"]),
    )

    diagram = render.mermaid(data)

    assert "n_alpha --> n_beta" in diagram
    assert "n_beta --> n_alpha" not in diagram


def test_mermaid_groups_by_stage_and_classes_by_strand() -> None:
    data = data_with(entry(), entry(key="beta", stage="evidence"))

    diagram = render.mermaid(data)

    assert 'subgraph stage_define["' in diagram
    assert 'subgraph stage_evidence["' in diagram
    assert "classDef adequacy" in diagram


def test_every_strand_has_a_visually_distinct_style() -> None:
    """Strand is carried by colour, so identical palettes would erase it silently."""
    styles = list(render.STRAND_STYLE.values())

    assert set(render.STRAND_STYLE) == set(mapdata.STRANDS)
    assert len(set(styles)) == len(styles)


def test_node_only_entries_get_no_click_target() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )

    diagram = render.mermaid(data)

    assert "click n_alpha" in diagram
    assert "click n_Thesis_Work_Area" not in diagram


def test_page_renders_a_card_per_card_entry_and_none_for_node_only() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable"),
    )

    page = render.page(data, live={"generated_at": "2026-08-19T09:00:00+00:00", "repos": {}})

    assert 'id="card-alpha"' in page
    assert 'id="card-Thesis-Work-Area"' not in page


def test_a_card_less_strand_names_its_entries_instead_of_emitting_a_bare_heading() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable",
              objective="Where the findings are written up."),
    )

    page = render.page(data, live={"generated_at": "t", "repos": {}})

    assert "Where the findings are written up." in page
    assert 'id="card-Thesis-Work-Area"' not in page


def test_feeds_row_does_not_link_to_a_node_only_entry() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )

    page = render.page(data, live={"generated_at": "t", "repos": {}})

    assert 'href="#card-Thesis-Work-Area"' not in page
    assert "Thesis-Work-Area" in page


def test_within_a_stage_entries_keep_their_authored_order() -> None:
    """Authored order, not alphabetical: the architecture candidates read A, B, C."""
    data = data_with(entry(key="zulu"), entry(key="alpha"))

    page = render.page(data, live={"generated_at": "t", "repos": {}})

    assert page.index('id="card-zulu"') < page.index('id="card-alpha"')


def test_external_links_are_marked() -> None:
    page = render.page(data_with(entry()), live={"generated_at": "t", "repos": {}})

    assert "\u2197" in page
    assert "opens GitHub" in page


def test_headline_is_rendered_with_its_source() -> None:
    data = data_with(
        entry(
            status="published",
            headline={"text": "13.3% fell to 2.2%.", "source": "probe v0.2.0, RESULTS.md"},
        )
    )

    page = render.page(data, live={"generated_at": "t", "repos": {}})

    assert "13.3% fell to 2.2%." in page
    assert "probe v0.2.0, RESULTS.md" in page


def test_live_push_date_is_rendered_when_known() -> None:
    """live.json holds only fields the page shows; pushed_at is one of them."""
    page = render.page(
        data_with(entry()),
        live={
            "generated_at": "t",
            "repos": {"alpha": {"visibility": "private", "pushed_at": "2026-08-19T08:00:00Z"}},
        },
    )

    assert "last commit 2026-08-19" in page


def test_missing_live_entry_is_badged_awaiting_refresh() -> None:
    page = render.page(data_with(entry()), live={"generated_at": "t", "repos": {}})

    assert "awaiting refresh" in page


def test_local_entry_is_badged_not_yet_published_and_has_no_github_link() -> None:
    page = render.page(
        data_with(entry(owner="local")), live={"generated_at": "t", "repos": {}}
    )

    assert "not yet published" in page
    assert "https://github.com/local/alpha" not in page


def test_absent_live_file_omits_the_footer_timestamp() -> None:
    page = render.page(data_with(entry()), live=None)

    assert "last refreshed" not in page.lower()


def test_prose_is_escaped_not_injected() -> None:
    page = render.page(
        data_with(entry(objective="<script>alert(1)</script>")),
        live={"generated_at": "t", "repos": {}},
    )

    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
