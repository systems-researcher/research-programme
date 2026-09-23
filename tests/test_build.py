# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for scripts.build: atomic write and live.json fold-in."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import build
from scripts.atomic import write_atomic


def _fake_data() -> SimpleNamespace:
    """Stub MapData: main only touches .repos once check/payload are patched."""
    return SimpleNamespace(repos=[])


def test_write_atomic_replaces_and_creates_parent(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "out.json"
    write_atomic(target, '{"ok": true}\n')
    assert target.read_text(encoding="utf-8") == '{"ok": true}\n'
    write_atomic(target, '{"ok": false}\n')
    assert target.read_text(encoding="utf-8") == '{"ok": false}\n'


def test_write_atomic_crash_before_replace_keeps_prior(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "out.json"
    target.write_text("PRIOR\n", encoding="utf-8")
    import scripts.atomic as atomic

    def boom(src, dst):
        raise RuntimeError("crash")

    monkeypatch.setattr(atomic.os, "replace", boom)
    with pytest.raises(RuntimeError):
        write_atomic(target, "NEW\n")
    assert target.read_text(encoding="utf-8") == "PRIOR\n"


def test_absent_live_warns_and_builds(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = tmp_path
    (root / "data").mkdir()
    readme = root / "README.md"
    readme.write_text(
        "head\n<!-- BEGIN:repos -->\nold\n<!-- END:repos -->\ntail\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(build, "ROOT", root)
    monkeypatch.setattr(build, "REPOS_YML", root / "repos.yml")

    fake = _fake_data()
    monkeypatch.setattr(build.mapdata, "load", lambda _p: fake)
    monkeypatch.setattr(build.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(
        build.render,
        "readme_block",
        lambda text, _data: text.replace("old", "new"),
    )
    monkeypatch.setattr(
        build.render,
        "payload",
        lambda _data, live: {"live_is_none": live is None, "strands": []},
    )

    assert build.main([]) == 0
    err = capsys.readouterr().err
    assert "absent" in err
    written = json.loads((root / "data" / "map.json").read_text(encoding="utf-8"))
    assert written["live_is_none"] is True


def test_truncated_live_warns_builds_without_live_fields(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = tmp_path
    (root / "data").mkdir()
    (root / "data" / "live.json").write_text("{truncated", encoding="utf-8")
    (root / "README.md").write_text(
        "h\n<!-- BEGIN:repos -->\nx\n<!-- END:repos -->\nt\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(build, "ROOT", root)
    monkeypatch.setattr(build, "REPOS_YML", root / "repos.yml")
    monkeypatch.setattr(build.mapdata, "load", lambda _p: _fake_data())
    monkeypatch.setattr(build.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(
        build.render, "readme_block", lambda text, _d: text
    )
    captured = {}

    def capture_payload(_data, live):
        captured["live"] = live
        return {"strands": []}

    monkeypatch.setattr(build.render, "payload", capture_payload)
    assert build.main([]) == 0
    assert captured["live"] is None
    err = capsys.readouterr().err
    assert "unreadable/corrupt" in err
    assert (root / "data" / "map.json").is_file()


def test_well_formed_live_is_passed_to_payload(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path
    (root / "data").mkdir()
    live_obj = {
        "generated_at": "t",
        "repos": {"alpha": {"visibility": "public", "homepage": "https://x.github.io/a/"}},
    }
    (root / "data" / "live.json").write_text(
        json.dumps(live_obj), encoding="utf-8"
    )
    (root / "README.md").write_text(
        "h\n<!-- BEGIN:repos -->\nx\n<!-- END:repos -->\nt\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(build, "ROOT", root)
    monkeypatch.setattr(build, "REPOS_YML", root / "repos.yml")
    monkeypatch.setattr(build.mapdata, "load", lambda _p: _fake_data())
    monkeypatch.setattr(build.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(build.render, "readme_block", lambda text, _d: text)
    captured = {}
    monkeypatch.setattr(
        build.render,
        "payload",
        lambda _d, live: captured.setdefault("live", live) or {"strands": []},
    )
    assert build.main([]) == 0
    assert captured["live"]["repos"]["alpha"]["visibility"] == "public"


def test_repos_shape_unusable_degrades(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = tmp_path
    (root / "data").mkdir()
    (root / "data" / "live.json").write_text(
        json.dumps({"generated_at": "t", "repos": ["not", "a", "dict"]}),
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "h\n<!-- BEGIN:repos -->\nx\n<!-- END:repos -->\nt\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(build, "ROOT", root)
    monkeypatch.setattr(build, "REPOS_YML", root / "repos.yml")
    monkeypatch.setattr(build.mapdata, "load", lambda _p: _fake_data())
    monkeypatch.setattr(build.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(build.render, "readme_block", lambda text, _d: text)
    captured = {}
    monkeypatch.setattr(
        build.render,
        "payload",
        lambda _d, live: captured.setdefault("live", live) or {"strands": []},
    )
    assert build.main([]) == 0
    assert captured["live"] is None
    assert "repos shape unusable" in capsys.readouterr().err


def test_non_dict_root_live_warns_corrupt_and_degrades(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = tmp_path
    (root / "data").mkdir()
    (root / "data" / "live.json").write_text(
        '["not", "an", "object"]', encoding="utf-8"
    )
    (root / "README.md").write_text(
        "h\n<!-- BEGIN:repos -->\nx\n<!-- END:repos -->\nt\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(build, "ROOT", root)
    monkeypatch.setattr(build, "REPOS_YML", root / "repos.yml")
    monkeypatch.setattr(build.mapdata, "load", lambda _p: _fake_data())
    monkeypatch.setattr(build.mapdata, "check", lambda _d: [])
    monkeypatch.setattr(build.render, "readme_block", lambda text, _d: text)
    captured = {}
    monkeypatch.setattr(
        build.render,
        "payload",
        lambda _d, live: captured.setdefault("live", live) or {"strands": []},
    )
    assert build.main([]) == 0
    assert captured["live"] is None
    assert "unreadable/corrupt" in capsys.readouterr().err
