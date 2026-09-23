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


def test_corrupt_previous_is_treated_as_empty_and_does_not_raise(
    tmp_path: Path, capsys
) -> None:
    live = tmp_path / "live.json"
    live.write_text("{not-json", encoding="utf-8")
    runner = fake_gh(
        {
            "repos/systems-researcher/alpha": {
                "visibility": "public",
                "pushed_at": "2026-08-19T08:00:00Z",
                "homepage": "https://example.github.io/alpha/",
            }
        }
    )

    result = refresh.collect(
        data_with(entry("alpha", "systems-researcher")), runner, previous=live
    )

    assert result.repos["alpha"]["visibility"] == "public"
    assert result.stale == []
    assert "unreadable/corrupt" in capsys.readouterr().err


def test_corrupt_previous_under_total_failure_treats_previous_as_empty(
    tmp_path: Path, capsys
) -> None:
    live = tmp_path / "live.json"
    live.write_text("{truncated", encoding="utf-8")
    data = data_with(entry("alpha", "systems-researcher"))

    result = refresh.collect(data, fake_gh({}), previous=live)

    assert result.repos == {}
    assert result.stale == ["alpha"]
    assert refresh.total_failure(data, result) is True
    assert "unreadable/corrupt" in capsys.readouterr().err


def test_total_failure_with_corrupt_previous_leaves_destination_untouched(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    dest = tmp_path / "live.json"
    prior = b"PRIOR_UNTOUCHED\n"
    dest.write_bytes(prior)

    data = data_with(entry("alpha", "systems-researcher"))
    monkeypatch.setattr(refresh, "LIVE_JSON", dest)
    monkeypatch.setattr(refresh.mapdata, "load", lambda _p: data)
    monkeypatch.setattr(refresh.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(
        refresh,
        "collect",
        lambda *_a, **_k: refresh.Refreshed(repos={}, stale=["alpha"]),
    )

    assert refresh.main([]) == 1
    assert dest.read_bytes() == prior


def test_corrupt_previous_warns_and_successful_repo_still_records(
    tmp_path: Path, capsys
) -> None:
    live = tmp_path / "live.json"
    live.write_text("{truncated", encoding="utf-8")
    runner = fake_gh(
        {
            "repos/systems-researcher/alpha": {
                "visibility": "public",
                "pushed_at": "2026-08-19T08:00:00Z",
                "homepage": "https://example.github.io/alpha/",
            }
        }
    )
    result = refresh.collect(
        data_with(entry("alpha", "systems-researcher")), runner, previous=live
    )
    assert result.stale == []
    assert result.repos["alpha"]["visibility"] == "public"
    err = capsys.readouterr().err
    assert "unreadable/corrupt" in err


def test_crash_before_replace_leaves_prior_live_json(
    tmp_path: Path, monkeypatch
) -> None:
    dest = tmp_path / "live.json"
    prior = '{"generated_at":"old","repos":{}}\n'
    dest.write_text(prior, encoding="utf-8")

    data = data_with(entry("alpha", "systems-researcher"))
    monkeypatch.setattr(refresh, "LIVE_JSON", dest)
    monkeypatch.setattr(refresh.mapdata, "load", lambda _p: data)
    monkeypatch.setattr(refresh.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(
        refresh,
        "collect",
        lambda *_a, **_k: refresh.Refreshed(
            repos={
                "alpha": {
                    "visibility": "public",
                    "pushed_at": "t",
                    "homepage": "https://example.github.io/a/",
                }
            },
            stale=[],
        ),
    )

    import scripts.atomic as atomic

    def boom(src, dst):
        raise RuntimeError("crash before replace")

    monkeypatch.setattr(atomic.os, "replace", boom)
    try:
        refresh.main([])
    except RuntimeError:
        pass
    assert dest.read_text(encoding="utf-8") == prior


def test_successful_refresh_write_is_full_payload_via_atomic(
    tmp_path: Path, monkeypatch
) -> None:
    dest = tmp_path / "live.json"
    data = data_with(entry("alpha", "systems-researcher"))
    monkeypatch.setattr(refresh, "LIVE_JSON", dest)
    monkeypatch.setattr(refresh.mapdata, "load", lambda _p: data)
    monkeypatch.setattr(refresh.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(
        refresh,
        "collect",
        lambda *_a, **_k: refresh.Refreshed(
            repos={
                "alpha": {
                    "visibility": "public",
                    "pushed_at": "t",
                    "homepage": "https://example.github.io/a/",
                }
            },
            stale=[],
        ),
    )
    assert refresh.main([]) == 0
    written = json.loads(dest.read_text(encoding="utf-8"))
    assert written["repos"]["alpha"]["visibility"] == "public"
    # Formatting contract: sort_keys + trailing newline
    raw = dest.read_text(encoding="utf-8")
    assert raw.endswith("\n")
    assert raw == json.dumps(written, indent=2, sort_keys=True) + "\n"


def test_refresh_module_does_not_call_write_text_for_live_output() -> None:
    import inspect
    from scripts import refresh as mod
    src = inspect.getsource(mod.main)
    assert "write_atomic" in src
    assert "LIVE_JSON.write_text" not in src
