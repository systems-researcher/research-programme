# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Contract tests for check / pages / refresh workflow YAML.

Workflow YAML cannot run locally. Two failure modes are silent at runtime:
renaming check or refresh stops the chain with no red job, and re-adding a
push trigger to pages.yml restores ungated deploys. PyYAML 1.1 loads the bare
key ``on`` as boolean True, so triggers are read from ``wf[True]``.
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"

BASE_PATH_EXPR = "/${{ github.event.repository.name }}/"


def load(name: str) -> dict:
    return yaml.safe_load((WF / name).read_text(encoding="utf-8"))


def test_workflow_names() -> None:
    assert load("check.yml")["name"] == "check"
    assert load("refresh.yml")["name"] == "refresh"


def test_pages_single_trigger_on_check() -> None:
    pages = load("pages.yml")
    on = pages[True]
    assert set(on) == {"workflow_run"}
    wr = on["workflow_run"]
    assert wr["workflows"] == ["check"]
    assert wr["types"] == ["completed"]
    assert wr["branches"] == ["main"]


def test_pages_build_if_and_checkout_ref() -> None:
    pages = load("pages.yml")
    build = pages["jobs"]["build"]
    cond = build["if"]
    assert "github.event.workflow_run.conclusion == 'success'" in cond
    assert "fromJSON" in cond
    assert "push" in cond and "workflow_dispatch" in cond and "workflow_run" in cond
    assert "github.event.workflow_run.head_sha == github.sha" in cond
    assert "pull_request" not in cond

    checkout = next(
        s for s in build["steps"] if s.get("uses", "").startswith("actions/checkout@")
    )
    assert checkout["with"]["ref"] == "${{ github.event.workflow_run.head_sha }}"


def test_pages_permissions_and_concurrency() -> None:
    pages = load("pages.yml")
    assert pages["permissions"] == {
        "contents": "read",
        "pages": "write",
        "id-token": "write",
    }
    assert pages["concurrency"] == {
        "group": "pages",
        "cancel-in-progress": False,
    }


def test_check_triggers_permissions_and_no_job_gates() -> None:
    check = load("check.yml")
    on = check[True]
    assert "push" in on
    assert "pull_request" in on
    assert "workflow_dispatch" in on
    wr = on["workflow_run"]
    assert wr["workflows"] == ["refresh"]
    assert wr["types"] == ["completed"]
    assert wr["branches"] == ["main"]
    assert check["permissions"] == {"contents": "read"}
    for job in check["jobs"].values():
        assert "permissions" not in job
        assert "if" not in job


def test_base_path_and_prefixed_site_urls() -> None:
    check = load("check.yml")
    pages = load("pages.yml")
    site = check["jobs"]["site"]
    assert site["env"]["BASE_PATH"] == BASE_PATH_EXPR

    build_step = next(s for s in pages["jobs"]["build"]["steps"] if s.get("name") == "Build")
    assert build_step["env"]["BASE_PATH"] == BASE_PATH_EXPR

    site_text = (WF / "check.yml").read_text(encoding="utf-8")
    assert "localhost:4173/" not in site_text
    assert 'localhost:4173${BASE_PATH}' in site_text
    # probe + both specs
    assert site_text.count("localhost:4173${BASE_PATH}") >= 3
