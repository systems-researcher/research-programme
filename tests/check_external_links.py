# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Fail if the site reaches any host other than the one it is allowed.

The page used to be one generated HTML file, so scraping it caught everything.
It is now a React app, so two things are checked: the reader-facing links in
data/map.json, and the resources the built entry HTML tells the browser to
fetch.

Only the entry HTML is scanned for fetches. Minified dependencies are full of
URL-shaped text — error-message links, XML namespace constants, doc pointers —
that no browser ever requests, so scanning every asset reports hosts that are
not contacted. A real third-party fetch (a CDN script, a font stylesheet)
would appear as a src/href in the entry HTML, which is what this reads.

Run after `python -m scripts.build` and `npm --prefix app run build`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# GitHub is the only host the programme links to. Fonts are bundled, not
# fetched, and Mermaid is an npm dependency rather than a CDN script — the
# whole point of both decisions is that this set stays at one entry.
ALLOWED = {"github.com"}

ROOT = Path(__file__).resolve().parent.parent
URL = re.compile(r"""https?://[^\s"'<>)]+""")
QUOTE = r'"([^"]*)"'


def hosts_in(text: str) -> set[str]:
    found = set()
    for url in URL.findall(text):
        try:
            found.add(urlparse(url).netloc)
        except ValueError:
            # Minified bundles contain URL-shaped fragments that are not URLs.
            # A string urlparse rejects is not a host the browser will fetch.
            continue
    return found


payload = json.loads((ROOT / "data" / "map.json").read_text(encoding="utf-8"))
links = sorted(
    entry["url"]
    for strand in payload["strands"]
    for entry in strand["entries"]
    if entry.get("url")
)
for link in links:
    print(link)

index = ROOT / "site" / "index.html"
if not index.exists():
    print("error: site/ is absent; run `npm --prefix app run build` first", file=sys.stderr)
    raise SystemExit(2)

html = index.read_text(encoding="utf-8")
fetched = {
    host
    for host in hosts_in(" ".join(re.findall(r"(?:src|href)=" + QUOTE, html)))
    if host
}
found = fetched | {urlparse(link).netloc for link in links}

unexpected = sorted(host for host in found if host not in ALLOWED)
if unexpected:
    print("unexpected hosts: " + ", ".join(unexpected), file=sys.stderr)
    raise SystemExit(1)
print(
    f"{len(links)} repository links, all to {sorted(ALLOWED)[0]}; "
    f"the built page fetches nothing off-origin"
)
