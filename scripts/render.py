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


# The CSS class each strand's nodes carry in the diagram, and the token stem
# that paints it. Colours live in design/tokens.css, never here: a Mermaid
# classDef writes inline "!important" onto every node, which outranks any
# stylesheet and would freeze the diagram in light mode. Emitting a bare
# "class" statement attaches the class without an inline style, so the same
# tokens drive the page and the diagram, and dark mode follows for free.
#
# Stems must differ: the strand is carried by colour, not by layout, so a
# shared stem would silently erase the distinction.
STRAND_CLASS = {
    "adequacy": "adequacy",
    "method-validation": "method_validation",
    "assembly": "assembly",
}
STRAND_TOKEN = {
    "adequacy": "adequacy",
    "method-validation": "method",
    "assembly": "assembly",
}

STATUS_LABELS = {
    "design": "design stage",
    "built-runs-pending": "built, runs pending",
    "released": "released",
    "results": "results in hand",
    "published": "published",
    "not-applicable": "",
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


def node_id(key: str) -> str:
    """A Mermaid-safe node id. Keys carry hyphens and mixed case; ids may not."""
    return "n_" + re.sub(r"[^A-Za-z0-9]", "_", key)


def mermaid(data: mapdata.MapData) -> str:
    """One subgraph per stage, strand carried by CSS class, edges from depends_on."""
    lines = ["graph LR"]
    for stage in STAGE_ORDER:
        members = [e for e in _ordered(data) if e["stage"] == stage]
        if not members:
            continue
        # The stage name alone. Its one-line explanation already renders as the
        # stage-note under the matching heading, and repeating it here only
        # widened every cluster to the length of a sentence.
        lines.append(f'  subgraph stage_{stage}["{stage.title()}"]')
        for member in members:
            lines.append(f'    {node_id(member["key"])}["{member["key"]}"]')
        lines.append("  end")

    for member in _ordered(data):
        for dependency in member.get("depends_on", []):
            lines.append(f'  {node_id(dependency)} --> {node_id(member["key"])}')

    for strand in STRAND_ORDER:
        members = [e for e in data.repos if e["strand"] == strand]
        if members:
            names = ",".join(node_id(m["key"]) for m in members)
            lines.append(f"  class {names} {STRAND_CLASS[strand]};")

    for member in data.repos:
        if member.get("render", "card") == "card":
            lines.append(f'  click {node_id(member["key"])} "#card-{member["key"]}"')

    return "\n".join(lines)


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
            item = {
                "key": key,
                "stage": entry["stage"],
                "card": is_card,
                "objective": _collapse(entry["objective"]),
            }
            if is_card:
                item.update(
                    {
                        "url": (
                            None
                            if entry["owner"] == "local"
                            else f"https://github.com/{entry['owner']}/{key}"
                        ),
                        "badges": _badges(entry, live_repos),
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
                        "dependsOn": _link_refs(entry.get("depends_on", []), data),
                        "feeds": _link_refs(inverted.get(key, []), data),
                    }
                )
            entries.append(item)

        strands.append(
            {
                "id": strand,
                "cssClass": STRAND_CLASS[strand],
                "token": STRAND_TOKEN[strand],
                "title": str(heading.get("title", strand)),
                "subtitle": _collapse(heading.get("subtitle", "")),
                "entries": entries,
            }
        )

    return {
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
        "diagram": mermaid(data),
        "refreshedAt": (live or {}).get("generated_at"),
    }
