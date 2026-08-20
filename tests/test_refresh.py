# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for the GitHub refresh. Never touches the network."""
from __future__ import annotations

import json
from pathlib import Path

from scripts import mapdata, refresh


def data_with(*entries: dict) -> mapdata.MapData:
    data = mapdata.MapData(programme={}, strands={}, stages={}, repos=list(entries))
    data.by_key = {entry["key"]: entry for entry in entries}
    return data


def entry(key: str, owner: str) -> dict:
    return {"key": key, "owner": owner}


def fake_gh(responses: dict[str, dict]):
    def runner(path: str) -> dict:
        if path not in responses:
            raise refresh.GhError(f"gh: {path}: Not Found")
        return responses[path]

    return runner


def test_local_entries_are_never_queried() -> None:
    calls = []

    def runner(path: str) -> dict:
        calls.append(path)
        return {}

    refresh.collect(data_with(entry("alpha", "local")), runner)

    assert calls == []


def test_successful_refresh_records_only_the_fields_the_page_renders() -> None:
    runner = fake_gh(
        {
            "repos/systems-researcher/alpha": {
                "description": "d",
                "visibility": "private",
                "default_branch": "main",
                "pushed_at": "2026-08-19T08:00:00Z",
                "stargazers_count": 3,
                "homepage": "https://example.github.io/alpha/",
            }
        }
    )

    result = refresh.collect(data_with(entry("alpha", "systems-researcher")), runner)

    assert result.repos["alpha"] == {
        "visibility": "private",
        "pushed_at": "2026-08-19T08:00:00Z",
        "homepage": "https://example.github.io/alpha/",
    }
    assert result.stale == []


def test_an_unreachable_repository_is_reported_stale_not_fatal() -> None:
    runner = fake_gh({})

    result = refresh.collect(data_with(entry("alpha", "systems-researcher")), runner)

    assert result.stale == ["alpha"]
    assert result.repos == {}


def test_total_failure_is_true_when_every_lookup_failed() -> None:
    data = data_with(entry("alpha", "systems-researcher"), entry("beta", "systems-researcher"))

    result = refresh.collect(data, fake_gh({}))

    assert refresh.total_failure(data, result) is True


def test_total_failure_is_false_when_only_local_entries_exist() -> None:
    data = data_with(entry("alpha", "local"))

    result = refresh.collect(data, fake_gh({}))

    assert refresh.total_failure(data, result) is False


def test_previous_entries_survive_a_failed_lookup(tmp_path: Path) -> None:
    live = tmp_path / "live.json"
    live.write_text(
        json.dumps(
            {
                "generated_at": "2026-01-01T00:00:00+00:00",
                "repos": {"alpha": {"visibility": "private", "pushed_at": "old"}},
            }
        ),
        encoding="utf-8",
    )

    result = refresh.collect(
        data_with(entry("alpha", "systems-researcher")), fake_gh({}), previous=live
    )

    assert result.repos["alpha"]["pushed_at"] == "old"
    assert result.stale == ["alpha"]
