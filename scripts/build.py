# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Validate repos.yml and render the site and README block."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from scripts import mapdata, render

ROOT = Path(__file__).resolve().parent.parent
REPOS_YML = ROOT / "repos.yml"


def write_atomic(path: Path, text: str) -> None:
    """Write via a temporary file in the same directory, then replace.

    A crashed build must never leave a half-written page, or a README with one
    marker and not the other.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate repos.yml and exit; write nothing",
    )
    args = parser.parse_args(argv)

    try:
        data = mapdata.load(REPOS_YML)
    except mapdata.MapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = mapdata.check(data)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"{len(errors)} problem(s) in {REPOS_YML.name}", file=sys.stderr)
        return 1

    if args.check:
        print(f"{REPOS_YML.name}: {len(data.repos)} entries, all nine rules pass")
        return 0

    live = None
    live_path = ROOT / "data" / "live.json"
    if live_path.exists():
        live = json.loads(live_path.read_text(encoding="utf-8"))
    else:
        print(
            "warning: data/live.json is absent; building without live GitHub fields",
            file=sys.stderr,
        )

    readme = ROOT / "README.md"
    try:
        rendered_readme = render.readme_block(readme.read_text(encoding="utf-8"), data)
    except render.RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    write_atomic(readme, rendered_readme)
    write_atomic(ROOT / "site" / "index.html", render.page(data, live))
    print(f"wrote README.md and site/index.html ({len(data.repos)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
