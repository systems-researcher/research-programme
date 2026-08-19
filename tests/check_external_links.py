# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Fail if the built page reaches any host other than the two it is allowed."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWED = {"cdn.jsdelivr.net", "github.com"}

page = Path("site/index.html").read_text(encoding="utf-8")
urls = sorted(set(re.findall(r"https?://[^\s\"'<>)]+", page)))
hosts = sorted({urlparse(url).netloc for url in urls})

for url in urls:
    print(url)

unexpected = [host for host in hosts if host not in ALLOWED]
if unexpected:
    print("unexpected hosts: " + ", ".join(unexpected), file=sys.stderr)
    raise SystemExit(1)
print(f"{len(urls)} URLs across {len(hosts)} hosts, all allowed")
