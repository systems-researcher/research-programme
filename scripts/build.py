# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Validate repos.yml and render the site and README block."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts import mapdata, render
from scripts.atomic import write_atomic

ROOT = Path(__file__).resolve().parent.parent
REPOS_YML = ROOT / "repos.yml"


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
        print(f"{REPOS_YML.name}: {len(data.repos)} entries, all ten rules pass")
        return 0

    live = None
    live_path = ROOT / "data" / "live.json"
    if live_path.exists():
        try:
            live = json.loads(live_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            print(
                "warning: data/live.json unreadable/corrupt; "
                "building without live GitHub fields",
                file=sys.stderr,
            )
            live = None
        if isinstance(live, dict):
            if "repos" in live and not isinstance(live.get("repos"), dict):
                print(
                    "warning: live.json repos shape unusable; "
                    "building without live GitHub fields",
                    file=sys.stderr,
                )
                live = None
        elif live is not None:
            # JSON root was not an object (array/string/number)
            print(
                "warning: data/live.json unreadable/corrupt; "
                "building without live GitHub fields",
                file=sys.stderr,
            )
            live = None
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
    # The app reads this and derives nothing: ordering, dependency inversion,
    # badges and card/node-only are all resolved here, under test. It is
    # committed so the deployment build needs Node only, never Python.
    write_atomic(
        ROOT / "data" / "map.json",
        json.dumps(render.payload(data, live), indent=2, ensure_ascii=False)
        + chr(10),
    )
    print(f"wrote README.md and data/map.json ({len(data.repos)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
