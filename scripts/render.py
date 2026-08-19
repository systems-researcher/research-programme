# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Pure rendering: MapData in, strings out. No file writes, no validation."""
from __future__ import annotations

import html
import re

from scripts import mapdata

BEGIN = "<!-- BEGIN:repos -->"
END = "<!-- END:repos -->"
STAGE_ORDER = mapdata.STAGES
STRAND_ORDER = mapdata.STRANDS

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

# One fill per strand. These must differ: the strand is carried by colour, not by
# layout, so identical palettes would silently erase the distinction.
STRAND_STYLE = {
    "adequacy": "fill:#e7effc,stroke:#3f6bb5,color:#10203a;",
    "method-validation": "fill:#f2ecfb,stroke:#7a5bb0,color:#241436;",
    "assembly": "fill:#eaf3ec,stroke:#4f8b62,color:#12291a;",
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
    """One subgraph per stage, strand carried by classDef, edges from depends_on."""
    lines = ["graph LR"]
    for stage in STAGE_ORDER:
        members = [e for e in _ordered(data) if e["stage"] == stage]
        if not members:
            continue
        label = html.escape(str(data.stages.get(stage, stage)))
        lines.append(f'  subgraph stage_{stage}["{stage.title()} — {label}"]')
        for member in members:
            lines.append(f'    {node_id(member["key"])}["{member["key"]}"]')
        lines.append("  end")

    for member in _ordered(data):
        for dependency in member.get("depends_on", []):
            lines.append(f'  {node_id(dependency)} --> {node_id(member["key"])}')

    for strand in STRAND_ORDER:
        members = [e for e in data.repos if e["strand"] == strand]
        if members:
            lines.append(f"  classDef {strand.replace('-', '_')} {STRAND_STYLE[strand]}")
            names = ",".join(node_id(m["key"]) for m in members)
            lines.append(f"  class {names} {strand.replace('-', '_')};")

    for member in data.repos:
        if member.get("render", "card") == "card":
            lines.append(f'  click {node_id(member["key"])} "#card-{member["key"]}"')

    return "\n".join(lines)


def _tidy(value: object) -> str:
    """Collapse the newlines a YAML folded scalar leaves behind, then escape."""
    return html.escape(" ".join(str(value).split()))


def _anchor(key: str, data: mapdata.MapData) -> str:
    """Link to a card, or plain text when the target renders no card."""
    target = data.by_key.get(key, {})
    if target.get("render", "card") == "node-only":
        return f'<span class="plain">{html.escape(key)}</span>'
    return f'<a href="#card-{html.escape(key)}">{html.escape(key)}</a>'


def _card(entry: dict, data: mapdata.MapData, inverted: dict, live: dict | None) -> str:
    key = entry["key"]
    live_repos = (live or {}).get("repos", {})
    known = key in live_repos

    if entry["owner"] == "local":
        badge, title = "not yet published", html.escape(key)
    else:
        badge = live_repos.get(key, {}).get("visibility", "awaiting refresh")
        if not known:
            badge = "awaiting refresh"
        url = f"https://github.com/{entry['owner']}/{key}"
        title = (
            f'<a href="{html.escape(url)}" rel="noopener">{html.escape(key)}'
            '<span class="ext" aria-hidden="true">\u2197</span>'
            '<span class="sr">(opens GitHub)</span></a>'
        )

    parts = [f'<article class="card" id="card-{html.escape(key)}">']
    parts.append(f"<h4>{title}</h4>")
    badges = [badge, STATUS_LABELS.get(entry["status"], "")]
    pushed = live_repos.get(key, {}).get("pushed_at")
    if pushed:
        badges.append(f"last commit {str(pushed)[:10]}")
    parts.append(
        '<p class="badges">'
        + "".join(f'<span class="badge">{html.escape(str(b))}</span>' for b in badges if b)
        + "</p>"
    )
    for label, field_name in (
        ("What it is for", "objective"),
        ("Question", "question"),
        ("Method", "method"),
    ):
        parts.append(f"<p><strong>{label}.</strong> {_tidy(entry[field_name])}</p>")

    headline = entry.get("headline")
    if headline:
        parts.append(
            '<p class="headline"><strong>Result.</strong> '
            f'{_tidy(headline["text"])} '
            f'<span class="source">Source: {_tidy(headline["source"])}</span></p>'
        )
    if entry.get("output"):
        parts.append(f'<p class="output">{_tidy(entry["output"])}</p>')

    depends = entry.get("depends_on", [])
    feeds_into = inverted.get(key, [])
    if depends:
        parts.append(
            '<p class="links"><strong>Depends on.</strong> '
            + ", ".join(_anchor(k, data) for k in depends)
            + "</p>"
        )
    if feeds_into:
        parts.append(
            '<p class="links"><strong>Feeds.</strong> '
            + ", ".join(_anchor(k, data) for k in feeds_into)
            + "</p>"
        )
    parts.append("</article>")
    return "\n".join(parts)


def page(data: mapdata.MapData, live: dict | None) -> str:
    inverted = mapdata.feeds(data)
    programme = data.programme

    sections = []
    for strand in STRAND_ORDER:
        members = [e for e in _ordered(data) if e["strand"] == strand]
        cards = [e for e in members if e.get("render", "card") == "card"]
        if not members:
            continue
        heading = data.strands.get(strand, {})
        sections.append(f'<section id="strand-{strand}">')
        sections.append(f'<h2>{html.escape(str(heading.get("title", strand)))}</h2>')
        sections.append(f'<p class="subtitle">{_tidy(heading.get("subtitle", ""))}</p>')
        if not cards:
            # Every member renders node-only (the thesis terminus). The section still
            # belongs on the page, but an empty one reads as a rendering fault, so
            # name the entries in a line instead of emitting a bare heading.
            for member in members:
                sections.append(
                    f'<p class="terminus"><strong>{html.escape(member["key"])}.</strong> '
                    f'{_tidy(member["objective"])}</p>'
                )
        for stage in STAGE_ORDER:
            in_stage = [e for e in cards if e["stage"] == stage]
            if not in_stage:
                continue
            sections.append(f"<h3>{stage.title()}</h3>")
            sections.append(f'<p class="stage-note">{_tidy(data.stages.get(stage, ""))}</p>')
            sections.extend(_card(e, data, inverted, live) for e in in_stage)
        sections.append("</section>")

    footer = []
    if live and live.get("generated_at"):
        footer.append(
            f'<p>Live repository data last refreshed {html.escape(str(live["generated_at"]))}.</p>'
        )
    footer.append(
        "<p>Repositories marked private are readable on request — contact the author.</p>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(str(programme.get("title", "Research programme")))}</title>
<style>
:root {{ --bg:#fbfbfd; --fg:#14161a; --muted:#5a6270; --line:#dfe3ea; --card:#ffffff; --accent:#2f4f8f; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#111318; --fg:#e8eaee; --muted:#98a1b0; --line:#272b33; --card:#171a20; --accent:#9db6f0; }}
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width: 62rem; margin: 0 auto; padding: 2rem 1.25rem 5rem; }}
h1 {{ font-size: 1.9rem; line-height:1.25; margin:0 0 .5rem; }}
h2 {{ font-size: 1.4rem; margin: 3rem 0 .25rem; padding-top:1.5rem; border-top:1px solid var(--line); }}
h3 {{ font-size: 1.05rem; margin: 2rem 0 .25rem; }}
.subtitle, .stage-note {{ color: var(--muted); margin:.25rem 0 1rem; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:1rem 1.15rem; margin:1rem 0; }}
.card h4 {{ margin:0 0 .5rem; font-size:1.05rem; }}
.ext {{ font-size:.75em; margin-left:.15em; }}
.sr {{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }}
.badges {{ margin:0 0 .75rem; }}
.badge {{ display:inline-block; font-size:.75rem; text-transform:uppercase; letter-spacing:.04em;
  border:1px solid var(--line); border-radius:1rem; padding:.1rem .6rem; margin-right:.4rem; color:var(--muted); }}
.card p {{ margin:.4rem 0; }}
.headline {{ border-left:3px solid var(--accent); padding-left:.75rem; }}
.source, .output {{ color:var(--muted); font-size:.85rem; }}
.links {{ font-size:.9rem; }}
.plain {{ color:var(--muted); }}
.terminus {{ color:var(--muted); }}
a {{ color:var(--accent); }}
#diagram {{ overflow-x:auto; border:1px solid var(--line); border-radius:.6rem; padding:1rem; background:var(--card); }}
footer {{ margin-top:4rem; padding-top:1.5rem; border-top:1px solid var(--line); color:var(--muted); font-size:.9rem; }}
</style>
</head>
<body>
<main>
<h1>{html.escape(str(programme.get("title", "")))}</h1>
<p>{html.escape(" ".join(str(programme.get("question", "")).split()))}</p>
<p><strong>{html.escape(" ".join(str(programme.get("move", "")).split()))}</strong></p>

<div id="diagram"><pre class="mermaid">
{mermaid(data)}
</pre></div>

{chr(10).join(sections)}

<footer>
{chr(10).join(footer)}
</footer>
</main>
<script type="module">
import mermaid from "{MERMAID_CDN}";
mermaid.initialize({{ startOnLoad: true, theme: window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default" }});
</script>
</body>
</html>
"""
