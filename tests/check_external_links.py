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

# Every host the page is allowed to send a reader to. Fonts are bundled and
# there is no CDN script, so nothing here is fetched on load — these are
# destinations a reader clicks.
#
# github.io is where the result sites live; the exact subdomain follows
# whoever owns the repository, so it is matched as a suffix rather than
# listed. Adding to this set should be a deliberate act: an unexpected host
# is how a tracking pixel or a dead redirect gets onto a research page.
ALLOWED = {"github.com", "doi.org"}
ALLOWED_SUFFIXES = ("github.io",)


def permitted(host: str) -> bool:
    return host in ALLOWED or host.endswith(ALLOWED_SUFFIXES)

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
# Everything the page can send a reader to: the repository, its result site,
# and the DOI resolver the citation block builds a link to.
links = set()
for strand in payload["strands"]:
    for entry in strand["entries"]:
        for url in (entry.get("url"), entry.get("site")):
            if url:
                links.add(url)
        if entry.get("paper"):
            links.add(f"https://doi.org/{entry['paper']['doi']}")
links = sorted(links)
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

unexpected = sorted(host for host in found if not permitted(host))
if unexpected:
    print("unexpected hosts: " + ", ".join(unexpected), file=sys.stderr)
    raise SystemExit(1)
print(
    f"{len(links)} outbound links across "
    f"{len(sorted({urlparse(link).netloc for link in links}))} permitted hosts; "
    f"the built page fetches nothing off-origin"
)
