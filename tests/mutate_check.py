# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Prove --check fails on a broken repos.yml. Restores the file on the way out."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPOS = Path("repos.yml")

# Four mutations across three rule classes: two on enumerated values (rule 2,
# stage and strand, because they are checked against different sets), one on
# owner shape (rule 7), and one dangling edge (rule 1) — the criterion the design
# spec names in its success criteria.
MUTATIONS = [
    ("stage: define", "stage: prototype"),
    ("strand: adequacy", "strand: nonsense"),
    ("owner: systems-researcher", "owner: not a name!"),
    ("depends_on: [epistemic-adequacy-probe]", "depends_on: [no-such-repository]"),
]

original = REPOS.read_text(encoding="utf-8")
failures = []
try:
    for old, new in MUTATIONS:
        assert old in original, f"mutation anchor missing: {old}"
        REPOS.write_text(original.replace(old, new, 1), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, "-m", "scripts.build", "--check"],
            capture_output=True,
            text=True,
        )
        if done.returncode == 0:
            failures.append(f"--check passed despite '{new}'")
        else:
            print(f"ok: '{new}' rejected -> {done.stderr.strip().splitlines()[0]}")
finally:
    REPOS.write_text(original, encoding="utf-8")

if failures:
    print("\n".join(failures), file=sys.stderr)
    raise SystemExit(1)
print(f"validator bites on all {len(MUTATIONS)} mutations")
