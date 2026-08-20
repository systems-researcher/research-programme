# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Pull live GitHub fields into data/live.json.

The only script that touches the network. Failure for one repository is never
fatal: its previous entry is kept and the key is reported stale on stderr.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from scripts import mapdata

ROOT = Path(__file__).resolve().parent.parent
REPOS_YML = ROOT / "repos.yml"
LIVE_JSON = ROOT / "data" / "live.json"
# Only fields the page actually renders. homepage is the repository's own
# result site: three of these repos publish their findings to GitHub Pages,
# and a reader sent "look at my research" wants the finding, not a file tree.
LIVE_FIELDS = ("visibility", "pushed_at", "homepage")


class GhError(Exception):
    """The gh CLI could not answer for one repository."""


@dataclass
class Refreshed:
    repos: dict[str, dict] = field(default_factory=dict)
    stale: list[str] = field(default_factory=list)


def gh_runner(path: str) -> dict:
    """Call the gh CLI and parse its JSON. Raises GhError on any failure."""
    try:
        completed = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GhError("gh is not installed or not on PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise GhError(f"gh api {path} failed: {exc.stderr.strip()}") from exc
    return json.loads(completed.stdout)


def collect(
    data: mapdata.MapData,
    runner: Callable[[str], dict] = gh_runner,
    previous: Path = LIVE_JSON,
) -> Refreshed:
    """Query every non-local entry. Keep the previous value for anything that fails."""
    old: dict[str, dict] = {}
    if previous and Path(previous).exists():
        old = json.loads(Path(previous).read_text(encoding="utf-8")).get("repos", {})

    result = Refreshed()
    for entry in data.repos:
        key, owner = entry["key"], entry["owner"]
        if owner == "local":
            continue
        try:
            payload = runner(f"repos/{owner}/{key}")
        except GhError:
            result.stale.append(key)
            if key in old:
                result.repos[key] = old[key]
            continue
        result.repos[key] = {name: payload.get(name) for name in LIVE_FIELDS}
    return result


def total_failure(data: mapdata.MapData, result: Refreshed) -> bool:
    """True when every repository that could have been queried failed.

    A refresh that reached nothing must not stamp a fresh generated_at: the
    footer would then publish a last-refreshed date describing no data at all.
    """
    queried = [entry for entry in data.repos if entry["owner"] != "local"]
    return bool(queried) and len(result.stale) == len(queried)


def main(argv: list[str] | None = None) -> int:
    try:
        data = mapdata.load(REPOS_YML)
    except mapdata.MapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Validate before reading any field. collect() indexes key and owner directly,
    # so an entry missing either would raise KeyError rather than say what is wrong
    # — and the documented workflow runs refresh before --check.
    errors = mapdata.check(data)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"{REPOS_YML.name} is not valid; fix it before refreshing", file=sys.stderr)
        return 2

    result = collect(data)
    if total_failure(data, result):
        print(
            "error: every GitHub lookup failed; data/live.json left untouched. "
            "Check `gh auth status` and your network.",
            file=sys.stderr,
        )
        return 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repos": result.repos,
    }
    LIVE_JSON.parent.mkdir(parents=True, exist_ok=True)
    LIVE_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"refreshed {len(result.repos)} repositories into {LIVE_JSON.name}")
    if result.stale:
        print(
            "stale (kept previous values): " + ", ".join(result.stale),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
