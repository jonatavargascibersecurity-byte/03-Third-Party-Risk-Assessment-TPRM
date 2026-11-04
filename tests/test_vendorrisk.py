"""Tests for inherent/residual scoring, concentration and exit plans."""

from dataclasses import replace
from datetime import date
from pathlib import Path

from tprm.dashboard import build_dashboard
from tprm.loader import load_tprm
from tprm.report import build_report
from tprm.vendorrisk import (
    assess_vendors,
    assessment_consistency_issues,
    build_exit_plans,
    build_exit_markdown,
    build_questionnaire_markdown,
    build_risk_markdown,
    concentration,
    contract_timing,
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


def test_assessments_match_canonical_risk_model():
    t = load_tprm(DATA_DIR)
    assert assessment_consistency_issues(t) == []
    broken = replace(t.assessments[0], residual_risk="Baixo")
    issues = assessment_consistency_issues(replace(t, assessments=[broken]))
    assert any("residual_risk" in issue for issue in issues)


def test_contract_state_is_derived_from_dates():
    t = load_tprm(DATA_DIR)
    contract = t.contracts_by_vendor["V-008"]
    assert contract.status == "Vencido"
    assert contract_timing(contract, date(2026, 11, 2))[0] == "Vencido"
    future = replace(contract, end_date="2027-06-01")
    assert contract_timing(future, date(2026, 11, 2))[0] == "Ativo"
    soon = replace(contract, end_date="2026-12-01")
    assert contract_timing(soon, date(2026, 11, 2))[0] == "Vencendo"


def test_expired_tier1_contract_is_an_exit_plan_gap():
    t = load_tprm(DATA_DIR)
    plans = build_exit_plans(t, date(2027, 2, 2))
    plan = next(p for p in plans if p.vendor_id == "V-001")
    assert plan.overall == "Gap"
    renewal = next(c for c in plan.checks if c.label == "Janela de renovacao monitorada")
    assert renewal.status == "Gap"
    assert "vencido" in renewal.detail.lower()


def test_report_and_dashboard_include_country_concentration():
    t = load_tprm(DATA_DIR)
    reference = date(2026, 11, 2)
    report = build_report(t, reference)
    dashboard = build_dashboard(t, as_of=reference)
    for output in (report, dashboard):
        assert "26.6%" in output
        assert "US" in output
        assert "ALERTA" in output or "SIM" in output


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
