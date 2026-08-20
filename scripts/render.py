# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Pure rendering: MapData in, the README table and the app payload out.

No file writes, no validation."""
from __future__ import annotations

import re


from scripts import mapdata

BEGIN = "<!-- BEGIN:repos -->"
END = "<!-- END:repos -->"
STAGE_ORDER = mapdata.STAGES
STRAND_ORDER = mapdata.STRANDS


# The token stem that paints each strand. Stems must differ: the strand is
# carried by colour, not by layout, so a shared stem would silently erase the
# distinction between two strands.
STRAND_TOKEN = {
    "adequacy": "adequacy",
    "method-validation": "method",
    "assembly": "assembly",
}

# STATUSES is ordered as the lifecycle runs: a study is designed, built, its
# code released, its runs produce results, and the result is published. The
# page relies on that order for the legend, so it is stated here rather than
# left as an accident of how the tuple was typed.
# One label per status, used verbatim by both the matrix cell and the legend.
# They used to differ — cells said "design", the legend said "design stage" —
# which read as two vocabularies for one thing. A cell has room for a single
# word, so the label IS the single word and the legend carries the
# explanation in STATUS_NOTES instead.
STATUS_LABELS = {
    "design": "design",
    "built-runs-pending": "built",
    "released": "released",
    "results": "results",
    "published": "published",
    "not-applicable": "",
}


# What each state means, for the legend. The label answers "what is this
# badge", the note answers "what has actually happened to the study".
STATUS_NOTES = {
    "design": "Written down and specified. No code that runs yet.",
    "built-runs-pending": "The instrument exists and runs. Not yet run for record.",
    "released": "Tagged and versioned. Others can depend on it.",
    "results": "Run for record. The numbers are in hand and being read.",
    "published": "The result is in the written record, in a venue or a frozen report.",
}


class RenderError(Exception):
    """The target document is not shaped the way rendering requires."""


def _ordered(data: mapdata.MapData) -> list[dict]:
    """Entries in strand order, then stage order, then the order authored in repos.yml.

    Authored order is the final tie-break, not alphabetical order: the three
    architecture candidates must read A, B, C, and their keys sort A, C, B.
    """
    position = {entry["key"]: index for index, entry in enumerate(data.repos)}
    return sorted(
        data.repos,
        key=lambda e: (
            STRAND_ORDER.index(e["strand"]),
            STAGE_ORDER.index(e["stage"]),
            position[e["key"]],
        ),
    )


def readme_table(data: mapdata.MapData) -> str:
    lines = [
        "| Repository | Stage | Status | What it is for |",
        "|---|---|---|---|",
    ]
    for entry in _ordered(data):
        objective = " ".join(str(entry["objective"]).split())
        lines.append(
            f"| `{entry['key']}` | {entry['stage']} | {entry['status']} | {objective} |"
        )
    return "\n".join(lines)


def readme_block(current: str, data: mapdata.MapData) -> str:
    """Replace the marked block in an existing README, leaving everything else alone."""
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        re.DOTALL,
    )
    if not pattern.search(current):
        raise RenderError(
            f"README.md has no {BEGIN} ... {END} block; add one before building"
        )
    replacement = f"{BEGIN}\n\n{readme_table(data)}\n\n{END}"
    return pattern.sub(lambda _: replacement, current, count=1)


def _collapse(value: object) -> str:
    """Collapse the newlines a YAML folded scalar leaves behind.

    Escaping is deliberately NOT done here. The README and the JSON payload
    both want the plain text; only the HTML renderer needs entities.
    """
    return " ".join(str(value).split())


# ---------------------------------------------------------------------------
# Payload for the React app.
#
# Every ordering, inversion, badge and card/node-only decision is resolved
# HERE, in Python, under the tests that already cover those rules. The app
# maps over what this produces and derives nothing, so a change to programme
# logic stays a change to tested Python rather than drifting into TypeScript.
# ---------------------------------------------------------------------------


def _badges(entry: dict, live_repos: dict) -> list[str]:
    """Visibility, status, and last-commit, in the order the card shows them."""
    key = entry["key"]
    if entry["owner"] == "local":
        first = "not yet published"
    else:
        first = live_repos.get(key, {}).get("visibility") or "awaiting refresh"
        if key not in live_repos:
            first = "awaiting refresh"

    badges = [first, STATUS_LABELS.get(entry["status"], "")]
    pushed = live_repos.get(key, {}).get("pushed_at")
    if pushed:
        badges.append(f"last commit {str(pushed)[:10]}")
    return [b for b in badges if b]


def _link_refs(keys: list[str], data: mapdata.MapData) -> list[dict]:
    """A dependency reference, already told whether it can be linked.

    node-only entries render no card, so there is nothing to anchor to; the
    app prints them as plain text. Deciding that here keeps the app from
    needing to know what "render" means.
    """
    refs = []
    for key in keys:
        target = data.by_key.get(key, {})
        refs.append({"key": key, "linkable": target.get("render", "card") == "card"})
    return refs


def payload(data: mapdata.MapData, live: dict | None) -> dict:
    """The whole page as data, in final render order.

    Text is collapsed but NOT html-escaped: React escapes on insertion, and
    pre-escaping would double-encode. The newline collapse still belongs here
    because it repairs YAML folded scalars, which React knows nothing about.
    """
    inverted = mapdata.feeds(data)
    live_repos = (live or {}).get("repos", {})
    ordered = _ordered(data)

    strands = []
    for strand in STRAND_ORDER:
        members = [e for e in ordered if e["strand"] == strand]
        if not members:
            continue
        heading = data.strands.get(strand, {})
        entries = []
        for entry in members:
            key = entry["key"]
            is_card = entry.get("render", "card") == "card"
            # Every entry carries its repository and its live badges, card or
            # not. `render: node-only` means "no card in the strand section",
            # not "no data": the written column is a real repository with a
            # visibility and a last commit, and dropping them left it on the
            # page as a bare name while every neighbour showed its state.
            item = {
                "key": key,
                "stage": entry["stage"],
                "card": is_card,
                "objective": _collapse(entry["objective"]),
                "url": (
                    None
                    if entry["owner"] == "local"
                    else f"https://github.com/{entry['owner']}/{key}"
                ),
                "badges": _badges(entry, live_repos),
                "dependsOn": _link_refs(entry.get("depends_on", []), data),
                "feeds": _link_refs(inverted.get(key, []), data),
            }
            if is_card:
                item.update(
                    {
                        "question": _collapse(entry["question"]),
                        "method": _collapse(entry["method"]),
                        "headline": (
                            {
                                "text": _collapse(entry["headline"]["text"]),
                                "source": _collapse(entry["headline"]["source"]),
                            }
                            if entry.get("headline")
                            else None
                        ),
                        "output": _collapse(entry["output"]) if entry.get("output") else None,
                        # The repository's own result site, when it publishes
                        # one. A reader wants the finding, not a file tree.
                        "site": (live_repos.get(key, {}).get("homepage") or None),
                        "paper": (
                            {
                                "title": _collapse(entry["paper"]["title"]),
                                "authors": [
                                    _collapse(a) for a in entry["paper"]["authors"]
                                ],
                                "venue": _collapse(entry["paper"]["venue"]),
                                "year": entry["paper"]["year"],
                                "doi": _collapse(entry["paper"]["doi"]),
                                "status": entry["paper"]["status"],
                            }
                            if entry.get("paper")
                            else None
                        ),
                    }
                )
            entries.append(item)

        strands.append(
            {
                "id": strand,
                "token": STRAND_TOKEN[strand],
                "title": str(heading.get("title", strand)),
                "subtitle": _collapse(heading.get("subtitle", "")),
                "entries": entries,
            }
        )

    return {
        # The lifecycle, in order, for the legend. Generated from the same
        # enum the validator uses, so the key on the page cannot document a
        # vocabulary the data does not have.
        "statuses": [
            {
                "id": status,
                "label": STATUS_LABELS[status],
                "note": STATUS_NOTES[status],
            }
            for status in mapdata.STATUSES
            if status != "not-applicable"
        ],
        "programme": {
            "title": str(data.programme.get("title", "Research programme")),
            "question": _collapse(data.programme.get("question", "")),
            "move": _collapse(data.programme.get("move", "")),
        },
        "stages": [
            {"id": stage, "title": stage.title(), "note": _collapse(data.stages.get(stage, ""))}
            for stage in STAGE_ORDER
        ],
        "strands": strands,
        "refreshedAt": (live or {}).get("generated_at"),
    }
