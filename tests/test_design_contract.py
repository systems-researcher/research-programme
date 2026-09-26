# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""The design contract in DESIGN.md must describe the shipped token surface.

DESIGN.md is the copy-me contract for later programme repositories, and it has
drifted twice: the diagram section kept describing Mermaid after the SVG
replacement (closed 2026-09-23), and the typography, colour, and radius
sections kept describing the pre-brand-kit system after the 2026-09 brand kit
landed. These assertions fail when the prose and app/src/index.css disagree.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
LICENSE = (ROOT / "LICENSE.md").read_text(encoding="utf-8")
INDEX_CSS = (ROOT / "app" / "src" / "index.css").read_text(encoding="utf-8")

# Claims that were true before the 2026-09 brand kit and are dead now. The
# synthetic document proves each constant matches a real dead claim, so a
# renamed or typoed constant cannot make the absence checks pass vacuously.
DEAD_CLAIMS = ("Geist", "@fontsource-variable", "0.625rem", "Neutral shadcn base")
SYNTHETIC_PRE_KIT_DOC = (
    "- **Display / body / UI:** Geist Variable, bundled via `@fontsource-variable`.\n"
    "- **Approach:** Neutral shadcn base.\n"
    "- **Border radius:** `--radius`, 0.625rem.\n"
)


def test_the_dead_claims_are_real_strings() -> None:
    for claim in DEAD_CLAIMS:
        assert claim in SYNTHETIC_PRE_KIT_DOC


def test_design_md_carries_no_dead_typography_or_colour_claims() -> None:
    for claim in DEAD_CLAIMS:
        assert claim not in DESIGN


def test_design_md_names_the_shipped_fonts() -> None:
    assert "--font-heading" in INDEX_CSS and "EB Garamond" in INDEX_CSS
    assert "--font-sans" in INDEX_CSS and "IBM Plex Sans" in INDEX_CSS
    assert "EB Garamond" in DESIGN
    assert "IBM Plex Sans" in DESIGN


def test_radius_claim_matches_the_token() -> None:
    match = re.search(r"--radius:\s*([^;]+);", INDEX_CSS)
    assert match, "--radius token missing from app/src/index.css"
    value = match.group(1).strip()
    assert f"`--radius`, {value}" in DESIGN, (
        f"DESIGN.md must state the shipped radius token value ({value})"
    )


def test_design_md_names_the_brand_palette() -> None:
    assert "Petrol" in DESIGN
    assert "Figure" in DESIGN or "brandkit" in DESIGN


def test_licence_attributes_the_bundled_fonts() -> None:
    assert "Geist" not in LICENSE
    for font in ("EB Garamond", "IBM Plex Sans"):
        assert font in LICENSE
