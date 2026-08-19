# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Load, validate, and invert the research-programme map data.

This module knows nothing about rendering. It turns repos.yml into a MapData
object, checks it against the nine rules in the design spec (§5), and derives
the reverse edge direction ("what feeds this") from the authored depends_on.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

STRANDS = ("adequacy", "method-validation", "assembly")
STAGES = ("define", "measure", "evidence", "architecture", "assembly")
STATUSES = (
    "design",
    "built-runs-pending",
    "released",
    "results",
    "published",
    "not-applicable",
)
RENDERS = ("card", "node-only")
REQUIRED = ("key", "owner", "strand", "stage", "objective", "question", "method", "status")
RESULT_STATUSES = ("results", "published")
TERMINUS = "Thesis-Work-Area"
OWNER_RE = re.compile(r"^[A-Za-z0-9-]+$")


class MapError(Exception):
    """repos.yml could not be read at all — syntax error or missing file."""


@dataclass
class MapData:
    programme: dict[str, Any]
    strands: dict[str, Any]
    stages: dict[str, Any]
    repos: list[dict[str, Any]]
    by_key: dict[str, dict[str, Any]] = field(default_factory=dict)


def load(path: Path) -> MapData:
    """Parse repos.yml. Raises MapError with line and column on a syntax error."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MapError(f"{path} does not exist") from exc
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise MapError(f"{path} is not valid YAML{where}: {exc}") from exc

    if not isinstance(raw, dict):
        raise MapError(f"{path} must be a mapping with programme, strands, stages, repos")

    repos = raw.get("repos") or []
    for entry in repos:
        entry.setdefault("render", "card")
        entry.setdefault("depends_on", [])

    data = MapData(
        programme=raw.get("programme") or {},
        strands=raw.get("strands") or {},
        stages=raw.get("stages") or {},
        repos=repos,
    )
    data.by_key = {entry["key"]: entry for entry in repos if "key" in entry}
    return data


def check(data: MapData) -> list[str]:
    """Return every rule violation as a readable string. Empty means valid."""
    errors: list[str] = []
    errors += _rule_3_required_fields(data)
    errors += _rule_1_unknown_dependency(data)
    errors += _rule_2_enumerated_values(data)
    errors += _rule_4_terminus_supplies_nothing(data)
    errors += _rule_5_headline_status(data)
    errors += _rule_6_headline_attribution(data)
    errors += _rule_7_owner_and_duplicates(data)
    errors += _rule_8_blocks_cover_every_entry(data)
    errors += _rule_9_acyclic(data)
    return errors


def _rule_3_required_fields(data: MapData) -> list[str]:
    errors = []
    for index, entry in enumerate(data.repos):
        name = entry.get("key") or f"entry #{index + 1}"
        for field_name in REQUIRED:
            if not entry.get(field_name):
                errors.append(f"{name}: missing required field '{field_name}'")
    return errors


def _rule_1_unknown_dependency(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        for dependency in entry.get("depends_on", []):
            if dependency not in data.by_key:
                errors.append(
                    f"{entry.get('key')}: depends_on names '{dependency}', which is not a key in repos.yml"
                )
    return errors


def _rule_2_enumerated_values(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        name = entry.get("key")
        for field_name, allowed in (
            ("strand", STRANDS),
            ("stage", STAGES),
            ("status", STATUSES),
            ("render", RENDERS),
        ):
            value = entry.get(field_name)
            if value is not None and value not in allowed:
                errors.append(
                    f"{name}: {field_name} is '{value}', not one of {', '.join(allowed)}"
                )
    return errors


def _rule_4_terminus_supplies_nothing(data: MapData) -> list[str]:
    return [
        f"{entry.get('key')}: depends_on names {TERMINUS}; the thesis consumes, it never supplies"
        for entry in data.repos
        if TERMINUS in entry.get("depends_on", [])
    ]


def _rule_5_headline_status(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        name = entry.get("key")
        status = entry.get("status")
        if entry.get("headline") and status not in RESULT_STATUSES:
            errors.append(
                f"{name}: has a headline but status is '{status}'; "
                f"only {' or '.join(RESULT_STATUSES)} may carry a measured result"
            )
        if status == "not-applicable" and entry.get("render") != "node-only":
            errors.append(
                f"{name}: status 'not-applicable' is permitted only on render: node-only entries"
            )
        if entry.get("render") == "node-only" and name != TERMINUS:
            errors.append(
                f"{name}: render 'node-only' is permitted only on {TERMINUS}; "
                "no study may be hidden from the cards"
            )
    return errors


def _rule_6_headline_attribution(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        headline = entry.get("headline")
        if not headline:
            continue
        if not isinstance(headline, dict):
            errors.append(f"{entry.get('key')}: headline must be a mapping of text and source")
            continue
        for part in ("text", "source"):
            if not headline.get(part):
                errors.append(
                    f"{entry.get('key')}: headline is missing '{part}'; "
                    "every published number must name the artefact it came from"
                )
    return errors


def _rule_7_owner_and_duplicates(data: MapData) -> list[str]:
    errors = []
    seen: set[str] = set()
    for entry in data.repos:
        key = entry.get("key")
        if key in seen:
            errors.append(f"duplicate key '{key}'")
        seen.add(key)

        owner = entry.get("owner")
        if owner and not OWNER_RE.match(str(owner)):
            errors.append(
                f"{key}: owner '{owner}' is not 'local' or a GitHub account name matching [A-Za-z0-9-]+"
            )
    return errors


def _rule_8_blocks_cover_every_entry(data: MapData) -> list[str]:
    errors = []
    for required_field in ("title", "question", "move"):
        if not data.programme.get(required_field):
            errors.append(f"programme.{required_field} is missing; the page header needs it")

    for entry in data.repos:
        key = entry.get("key")
        stage = entry.get("stage")
        strand = entry.get("strand")
        if stage and stage not in data.stages:
            errors.append(
                f"{key}: stage '{stage}' has no line in the stages block, "
                "so its section would render with no explanation"
            )
        if strand and strand not in data.strands:
            errors.append(
                f"{key}: strand '{strand}' has no entry in the strands block, "
                "so its section would render with no heading"
            )
    return errors


def _rule_9_acyclic(data: MapData) -> list[str]:
    """Depth-first search reporting the full path of the first cycle found per root."""
    errors = []
    visiting: list[str] = []
    done: set[str] = set()

    def walk(key: str) -> None:
        if key in done:
            return
        if key in visiting:
            cycle = visiting[visiting.index(key) :] + [key]
            errors.append("depends_on cycle: " + " -> ".join(cycle))
            return
        visiting.append(key)
        for dependency in data.by_key.get(key, {}).get("depends_on", []):
            if dependency in data.by_key:
                walk(dependency)
        visiting.pop()
        done.add(key)

    for entry in data.repos:
        walk(entry.get("key"))
    return errors


def feeds(data: MapData) -> dict[str, list[str]]:
    """Invert depends_on. feeds[a] lists every key that declares a dependency on a."""
    inverted: dict[str, list[str]] = {entry["key"]: [] for entry in data.repos}
    for entry in data.repos:
        for dependency in entry.get("depends_on", []):
            if dependency in inverted:
                inverted[dependency].append(entry["key"])
    return {key: sorted(value) for key, value in inverted.items()}
