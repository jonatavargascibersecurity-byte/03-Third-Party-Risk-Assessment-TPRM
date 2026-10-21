"""Tests for TPRM scoring and data."""

from pathlib import Path

from tprm.loader import load_tprm
from tprm.scales import compute_vendor_risk

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_compute_vendor_risk():
    assert compute_vendor_risk("Crítico", 0, 0) == "Alto"
    assert compute_vendor_risk("Crítico", 2, 0) == "Crítico"
    assert compute_vendor_risk("Moderado", 0, 0) == "Moderado"
    assert compute_vendor_risk("Baixo", 0, 0) == "Baixo"
    assert compute_vendor_risk("Moderado", 1, 1) == "Alto"

def test_data_loads_and_validates():
    t = load_tprm(DATA_DIR)
    assert len(t.vendors) >= 5
    assert len(t.findings) >= 5
    assert t.validate() == []


def test_every_vendor_has_risk():
    t = load_tprm(DATA_DIR)
    levels = {"Crítico", "Alto", "Moderado", "Baixo"}
    for v in t.vendors:
        assert t.vendor_risk(v) in levels


def test_findings_link_to_vendors():
    t = load_tprm(DATA_DIR)
    vendor_ids = {v.vendor_id for v in t.vendors}
    for f in t.findings:
        assert f.vendor_id in vendor_ids
