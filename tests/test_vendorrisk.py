"""Tests for inherent/residual scoring, concentration and exit plans."""

from datetime import date
from pathlib import Path

from tprm.loader import load_tprm
from tprm.vendorrisk import (
    assess_vendors,
    build_exit_plans,
    build_exit_markdown,
    build_questionnaire_markdown,
    build_risk_markdown,
    concentration,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_questionnaire_and_residual_scoring():
    t = load_tprm(DATA_DIR)
    details = {d.vendor_id: d for d in assess_vendors(t)}
    assert len(details) == 10
    assert details["V-010"].compliance_pct == 100.0
    assert details["V-004"].compliance_pct == 70.0
    assert details["V-004"].residual_level == "Crítico"
    for detail in details.values():
        assert detail.residual_score <= detail.inherent_score
        assert detail.inherent_level in {"Crítico", "Alto", "Moderado", "Baixo"}


def test_concentration_by_country_flags_us():
    t = load_tprm(DATA_DIR)
    details = assess_vendors(t)
    rows = concentration(details, dimension="country")
    us = next(r for r in rows if r.category == "US")
    assert us.flagged
    assert us.vendors == 3


def test_tier1_exit_plans_have_contract_and_pending_items():
    t = load_tprm(DATA_DIR)
    plans = build_exit_plans(t, date(2026, 11, 2))
    assert len(plans) == 5
    assert all(p.overall in {"OK", "Gap"} for p in plans)
    assert all(len(p.pending) >= 2 for p in plans)
    md = build_exit_markdown(plans, date(2026, 11, 2))
    assert "DORA" in md
    assert "Runbook de saida" in md


def test_markdown_outputs():
    t = load_tprm(DATA_DIR)
    details = assess_vendors(t)
    rows = concentration(details)
    countries = concentration(details, dimension="country")
    risk_md = build_risk_markdown(details, rows, countries)
    assert "Inerente x Residual" in risk_md
    assert "Concentracao por pais" in risk_md
    q_md = build_questionnaire_markdown(t, details)
    assert "Due Diligence" in q_md
    assert "V-004" in q_md
