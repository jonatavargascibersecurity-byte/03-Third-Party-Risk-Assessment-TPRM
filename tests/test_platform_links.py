"""Guard the explicit links to real platform content.

The repository must point to the actual room/course/module, not to a platform
home page. These tests fail if a link is removed or replaced by a generic URL.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLATFORM_URLS = [
    "https://tryhackme.com/room/cybergovernanceregulation",
    "https://tryhackme.com/room/seriskmanagement",
    "https://app.letsdefend.io/training/lessons/risk-management",
    "https://app.letsdefend.io/training/lessons/security-product-selection",
    "https://academy.hackthebox.com/course/preview/supply-chain-attacks",
]


def test_readme_references_real_platform_content():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for url in PLATFORM_URLS:
        assert url in readme


def test_platforms_mapping_links_content_to_artefacts():
    doc = (ROOT / "PLATFORMS.md").read_text(encoding="utf-8")
    for url in PLATFORM_URLS:
        assert url in doc
    for artefact in (
        "data/questionnaire.csv",
        "src/tprm/vendorrisk.py",
        "src/tprm/scales.py",
        "data/contracts.csv",
    ):
        assert artefact in doc


def test_evidence_writeup_exists_and_cites_every_link():
    path = ROOT / "learning-log" / "2026-11-03-tprm-platform-evidence.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for url in PLATFORM_URLS:
        assert url in text
