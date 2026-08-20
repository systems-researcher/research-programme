# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for the README block, the diagram source, and the app payload."""
from __future__ import annotations

import re
from pathlib import Path

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
    assert "class n_alpha,n_beta adequacy;" in diagram


def test_diagram_carries_no_inline_colour() -> None:
    """A Mermaid classDef writes inline '!important' onto every node, which
    outranks the stylesheet and freezes the diagram in light mode. The strand
    must travel as a bare class so design/tokens.css can repaint it."""
    diagram = render.mermaid(data_with(entry()))

    assert "classDef" not in diagram
    assert "fill:#" not in diagram


def test_every_strand_has_a_visually_distinct_style() -> None:
    """Strand is carried by colour, so identical palettes would erase it silently."""
    assert set(render.STRAND_CLASS) == set(mapdata.STRANDS)
    assert set(render.STRAND_TOKEN) == set(mapdata.STRANDS)
    assert len(set(render.STRAND_CLASS.values())) == len(render.STRAND_CLASS)
    assert len(set(render.STRAND_TOKEN.values())) == len(render.STRAND_TOKEN)


def test_every_strand_token_resolves_in_both_colour_schemes() -> None:
    """The dark block must redefine every strand colour the light block sets,
    or the diagram silently keeps its light fills on a dark page."""
    css = (
        Path(__file__).resolve().parent.parent / "app" / "src" / "index.css"
    ).read_text(encoding="utf-8")

    # The stylesheet holds more than one :root / .dark pair (shadcn writes its
    # own, the programme adds strand colours after it), so collect the bodies
    # of every block of each kind rather than splitting on the first match.
    def bodies(selector: str) -> str:
        pattern = "^" + re.escape(selector) + r" \{$"
        found = []
        for match in re.finditer(pattern, css, re.MULTILINE):
            end = css.index("\n}", match.end())
            found.append(css[match.end() : end])
        assert found, f"no {selector} block in the stylesheet"
        return "\n".join(found)

    light, dark = bodies(":root"), bodies(".dark")

    for token in render.STRAND_TOKEN.values():
        for part in ("fill", "line"):
            assert f"--strand-{token}-{part}:" in light
            assert f"--strand-{token}-{part}:" in dark


def test_node_only_entries_get_no_click_target() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )

    diagram = render.mermaid(data)

    assert "click n_alpha" in diagram
    assert "click n_Thesis_Work_Area" not in diagram


# ---------------------------------------------------------------------------
# payload(): the data the React app renders.
#
# These replace the assertions that used to run against the generated HTML.
# The app derives nothing, so every ordering, inversion and badge rule is
# still a Python rule and still tested here — only the surface changed.
# ---------------------------------------------------------------------------


def entries_of(payload: dict) -> list[dict]:
    return [e for strand in payload["strands"] for e in strand["entries"]]


def find(payload: dict, key: str) -> dict:
    return next(e for e in entries_of(payload) if e["key"] == key)


LIVE_EMPTY = {"generated_at": "t", "repos": {}}


def test_payload_marks_node_only_entries_as_rendering_no_card() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable"),
    )

    payload = render.payload(data, LIVE_EMPTY)

    assert find(payload, "alpha")["card"] is True
    assert find(payload, "Thesis-Work-Area")["card"] is False


def test_a_card_less_strand_still_carries_its_entries_and_their_objective() -> None:
    """The strand keeps its section; the app names the entries instead of
    emitting a heading over nothing."""
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable",
              objective="Where the findings are written up."),
    )

    payload = render.payload(data, LIVE_EMPTY)
    assembly = next(s for s in payload["strands"] if s["id"] == "assembly")

    assert [e["key"] for e in assembly["entries"]] == ["Thesis-Work-Area"]
    assert assembly["entries"][0]["objective"] == "Where the findings are written up."


def test_a_reference_to_a_node_only_entry_is_not_linkable() -> None:
    """node-only entries render no card, so an anchor would go nowhere."""
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )

    payload = render.payload(data, LIVE_EMPTY)
    feeds = find(payload, "alpha")["feeds"]

    assert {"key": "Thesis-Work-Area", "linkable": False} in feeds


def test_a_reference_to_a_card_entry_is_linkable() -> None:
    data = data_with(entry(), entry(key="beta", stage="evidence", depends_on=["alpha"]))

    payload = render.payload(data, LIVE_EMPTY)

    assert find(payload, "beta")["dependsOn"] == [{"key": "alpha", "linkable": True}]
    assert find(payload, "alpha")["feeds"] == [{"key": "beta", "linkable": True}]


def test_within_a_stage_entries_keep_their_authored_order() -> None:
    """Authored order, not alphabetical: the architecture candidates read A, B, C."""
    data = data_with(entry(key="zulu"), entry(key="alpha"))

    payload = render.payload(data, LIVE_EMPTY)

    assert [e["key"] for e in entries_of(payload)] == ["zulu", "alpha"]


def test_strands_and_stages_arrive_in_programme_order() -> None:
    data = data_with(
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable"),
        entry(),
    )

    payload = render.payload(data, LIVE_EMPTY)

    assert [s["id"] for s in payload["strands"]] == ["adequacy", "assembly"]
    assert [s["id"] for s in payload["stages"]] == list(mapdata.STAGES)


def test_published_entry_carries_its_github_url() -> None:
    payload = render.payload(data_with(entry()), LIVE_EMPTY)

    assert find(payload, "alpha")["url"] == "https://github.com/systems-researcher/alpha"


def test_local_entry_is_badged_not_yet_published_and_has_no_url() -> None:
    payload = render.payload(data_with(entry(owner="local")), LIVE_EMPTY)
    alpha = find(payload, "alpha")

    assert alpha["url"] is None
    assert "not yet published" in alpha["badges"]


def test_missing_live_entry_is_badged_awaiting_refresh() -> None:
    payload = render.payload(data_with(entry()), LIVE_EMPTY)

    assert "awaiting refresh" in find(payload, "alpha")["badges"]


def test_live_visibility_and_push_date_are_carried_as_badges() -> None:
    """live.json holds only fields the page shows; pushed_at is one of them."""
    payload = render.payload(
        data_with(entry()),
        {
            "generated_at": "t",
            "repos": {"alpha": {"visibility": "private", "pushed_at": "2026-08-19T08:00:00Z"}},
        },
    )
    badges = find(payload, "alpha")["badges"]

    assert "private" in badges
    assert "last commit 2026-08-19" in badges


def test_status_is_badged_in_words_not_in_its_slug() -> None:
    payload = render.payload(data_with(entry(status="built-runs-pending")), LIVE_EMPTY)

    assert "built, runs pending" in find(payload, "alpha")["badges"]


def test_headline_is_carried_with_its_source() -> None:
    payload = render.payload(
        data_with(
            entry(
                status="published",
                headline={"text": "13.3% fell to 2.2%.", "source": "probe v0.2.0, RESULTS.md"},
            )
        ),
        LIVE_EMPTY,
    )

    assert find(payload, "alpha")["headline"] == {
        "text": "13.3% fell to 2.2%.",
        "source": "probe v0.2.0, RESULTS.md",
    }


def test_absent_live_file_leaves_the_refresh_stamp_unset() -> None:
    payload = render.payload(data_with(entry()), live=None)

    assert payload["refreshedAt"] is None


def test_folded_scalars_are_collapsed_but_not_escaped() -> None:
    """React escapes on insertion, so pre-escaping here would double-encode.
    The newline collapse still belongs in Python: it repairs YAML folding,
    which the app knows nothing about."""
    payload = render.payload(
        data_with(entry(objective="one\ntwo   three", question="A & B", method="m")),
        LIVE_EMPTY,
    )
    alpha = find(payload, "alpha")

    assert alpha["objective"] == "one two three"
    assert alpha["question"] == "A & B"


def test_payload_carries_the_diagram_source_for_the_app_to_draw() -> None:
    payload = render.payload(data_with(entry()), LIVE_EMPTY)

    assert payload["diagram"] == render.mermaid(data_with(entry()))
    assert "classDef" not in payload["diagram"]


def test_every_click_target_in_the_diagram_resolves_to_a_card() -> None:
    """A click on a node scrolls to `#card-<key>`; a target with no card is a
    dead link the reader can only discover by clicking it."""
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable"),
    )
    payload = render.payload(data, LIVE_EMPTY)

    targets = set(re.findall(r'click \S+ "#card-([^"]+)"', payload["diagram"]))
    cards = {e["key"] for e in entries_of(payload) if e["card"]}

    assert targets <= cards
    assert targets == {"alpha"}
