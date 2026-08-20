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
        stages={"define": "d", "evidence": "e", "release": "a"},
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


def test_every_strand_has_a_visually_distinct_style() -> None:
    """Strand is carried by colour, so identical palettes would erase it silently."""
    assert set(render.STRAND_TOKEN) == set(mapdata.STRANDS)
    assert len(set(render.STRAND_TOKEN.values())) == len(render.STRAND_TOKEN)


def test_every_strand_token_resolves_in_both_colour_schemes() -> None:
    """The dark block must redefine every strand colour the light block sets,
    or the matrix silently keeps its light accents on a dark page."""
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

    # One value per strand now: the cell tints are derived from the line
    # colour with colour-mix, so there is no separate fill to keep in step.
    for token in render.STRAND_TOKEN.values():
        assert f"--strand-{token}-line:" in light
        assert f"--strand-{token}-line:" in dark


# ---------------------------------------------------------------------------
# payload(): the data the React app renders.
#
# The app derives nothing, so every ordering, inversion and badge rule is a
# Python rule and is tested here.
# ---------------------------------------------------------------------------


def entries_of(payload: dict) -> list[dict]:
    return [e for strand in payload["strands"] for e in strand["entries"]]


def find(payload: dict, key: str) -> dict:
    return next(e for e in entries_of(payload) if e["key"] == key)


LIVE_EMPTY = {"generated_at": "t", "repos": {}}


def test_payload_marks_node_only_entries_as_rendering_no_card() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="release",
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
        entry(key="Thesis-Work-Area", strand="assembly", stage="release",
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
        entry(key="Thesis-Work-Area", strand="assembly", stage="release",
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
        entry(key="Thesis-Work-Area", strand="assembly", stage="release",
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
    """The badge says what the reader sees in the legend, not the enum key."""
    payload = render.payload(data_with(entry(status="built-runs-pending")), LIVE_EMPTY)

    badges = find(payload, "alpha")["badges"]

    assert "built" in badges
    assert "built-runs-pending" not in badges


def test_a_status_label_is_one_word_so_a_cell_and_the_legend_can_share_it() -> None:
    """The cell showed "design" while the legend said "design stage", which
    read as two vocabularies for one thing. The fix was one label used in both
    places — which only works while the label fits in a cell.

    A multi-word label would push the matrix back into abbreviating, and the
    two vocabularies would silently diverge again. The explanation belongs in
    STATUS_NOTES, which the legend shows and the cell does not.
    """
    for status, label in render.STATUS_LABELS.items():
        if not label:
            continue
        assert " " not in label and "," not in label, (
            f"{status}: label {label!r} will not fit a matrix cell; "
            "put the explanation in STATUS_NOTES instead"
        )


def test_every_labelled_status_explains_itself_in_the_legend() -> None:
    """The cell shows the word; the legend is the only place that says what
    the word means, so a state without a note is undocumented."""
    for status in mapdata.STATUSES:
        if render.STATUS_LABELS[status]:
            assert render.STATUS_NOTES.get(status), f"{status} has no explanation"


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


def test_every_entry_lands_in_a_stage_the_page_renders() -> None:
    """The matrix draws one column per stage in payload["stages"]. An entry
    whose stage is not among them would be silently dropped from the page —
    present in repos.yml, absent from the map, with nothing to show it went
    missing."""
    data = data_with(
        entry(),
        entry(key="beta", stage="evidence"),
        entry(key="Thesis-Work-Area", strand="assembly", stage="release",
              render="node-only", status="not-applicable"),
    )
    payload = render.payload(data, LIVE_EMPTY)

    columns = {stage["id"] for stage in payload["stages"]}
    placed = {e["key"] for e in entries_of(payload) if e["stage"] in columns}

    assert placed == {"alpha", "beta", "Thesis-Work-Area"}


def test_every_strand_carries_the_token_that_colours_its_row() -> None:
    """Strand colour is how the matrix distinguishes the rows; a strand
    arriving without its token stem would render an uncoloured row."""
    data = data_with(entry())
    payload = render.payload(data, LIVE_EMPTY)

    for strand in payload["strands"]:
        assert strand["token"] in render.STRAND_TOKEN.values()


def test_a_published_result_site_is_carried_when_github_reports_one() -> None:
    """Three of these repositories publish their findings to GitHub Pages.
    The reader wants the finding, so the map has to be able to link it."""
    payload = render.payload(
        data_with(entry()),
        {
            "generated_at": "t",
            "repos": {"alpha": {"visibility": "public", "homepage": "https://x.github.io/alpha/"}},
        },
    )

    assert find(payload, "alpha")["site"] == "https://x.github.io/alpha/"


def test_an_empty_homepage_is_carried_as_absent_not_as_a_blank_link() -> None:
    """GitHub returns "" rather than null for a repository with no homepage,
    which would render as a link to nowhere."""
    payload = render.payload(
        data_with(entry()),
        {"generated_at": "t", "repos": {"alpha": {"visibility": "public", "homepage": ""}}},
    )

    assert find(payload, "alpha")["site"] is None


def test_a_paper_is_carried_whole_so_the_page_can_cite_it() -> None:
    payload = render.payload(
        data_with(
            entry(
                status="published",
                paper={
                    "title": "Models as Governed Interfaces",
                    "authors": ["Gower, Jason D.", "Ji, Siyuan"],
                    "venue": "Proceedings of MODELS 2026, NIER Track",
                    "year": 2026,
                    "doi": "10.1145/3822455.3838783",
                    "status": "accepted",
                },
            )
        ),
        LIVE_EMPTY,
    )

    assert find(payload, "alpha")["paper"] == {
        "title": "Models as Governed Interfaces",
        "authors": ["Gower, Jason D.", "Ji, Siyuan"],
        "venue": "Proceedings of MODELS 2026, NIER Track",
        "year": 2026,
        "doi": "10.1145/3822455.3838783",
        "status": "accepted",
    }


def test_an_entry_without_a_paper_carries_none() -> None:
    payload = render.payload(data_with(entry()), LIVE_EMPTY)

    assert find(payload, "alpha")["paper"] is None


def test_every_status_has_a_label_the_page_can_show() -> None:
    """A status with no label renders as an empty badge: the reader sees a
    study with no state at all, and nothing anywhere reports the omission."""
    for status in mapdata.STATUSES:
        assert status in render.STATUS_LABELS, f"{status} has no label"

    labelled = [s for s in mapdata.STATUSES if render.STATUS_LABELS[s]]
    assert "not-applicable" not in labelled, (
        "the terminus is deliberately unlabelled; it is not a study with a state"
    )
    assert len(labelled) == len(mapdata.STATUSES) - 1


def test_the_legend_can_be_built_from_the_status_vocabulary() -> None:
    """The legend documents the lifecycle, so it must be generated from the
    enum rather than hand-written beside it, or the two drift apart."""
    payload = render.payload(data_with(entry()), LIVE_EMPTY)

    assert [item["id"] for item in payload["statuses"]] == [
        s for s in mapdata.STATUSES if s != "not-applicable"
    ]
    assert all(item["label"] for item in payload["statuses"])


def test_a_node_only_entry_still_carries_its_repository_and_badges() -> None:
    """`render: node-only` means no card in the strand section, not no data.
    The written column is a real repository with a visibility and a last
    commit, and dropping them left it on the page as a bare name while every
    neighbour showed its state."""
    data = data_with(
        entry(),
        entry(key="publications", strand="assembly", stage="release",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )
    payload = render.payload(
        data,
        {
            "generated_at": "t",
            "repos": {"publications": {"visibility": "private", "pushed_at": "2026-08-19T08:00:00Z"}},
        },
    )
    column = find(payload, "publications")

    assert column["card"] is False
    assert column["url"] == "https://github.com/systems-researcher/publications"
    assert "private" in column["badges"]
    assert "last commit 2026-08-19" in column["badges"]
    assert [ref["key"] for ref in column["dependsOn"]] == ["alpha"]


def test_a_node_only_entry_carries_no_study_fields() -> None:
    """It is not a study: it has no question, method, or result to show."""
    data = data_with(
        entry(),
        entry(key="publications", strand="assembly", stage="release",
              render="node-only", status="not-applicable"),
    )
    column = find(render.payload(data, LIVE_EMPTY), "publications")

    for field_name in ("question", "method", "headline", "paper", "site"):
        assert field_name not in column
