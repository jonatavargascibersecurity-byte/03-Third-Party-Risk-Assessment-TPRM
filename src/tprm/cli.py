"""CLI for TPRM."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .loader import DataError, load_tprm
from .report import build_report
from .dashboard import write_dashboard
from .vendorrisk import (
    assess_vendors,
    assessment_consistency_issues,
    build_exit_markdown,
    build_exit_plans,
    build_questionnaire_markdown,
    build_risk_markdown,
    concentration,
    contract_timing,
)

DEFAULT_DATA_DIR = "data"
DEFAULT_OUT_DIR = "build"


def _reference(args):
    raw = getattr(args, "as_of", None)
    if not raw:
        return date.today()
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise DataError(
            f"invalid --as-of date: {raw!r} (expected YYYY-MM-DD)"
        ) from exc


def cmd_validate(args):
    t = load_tprm(args.data)
    issues = t.validate() + assessment_consistency_issues(t)
    if not issues:
        print("OK - TPRM data quality checks passed.")
        return 0
    for i, issue in enumerate(issues, 1):
        print(f"{i:>2}. {issue}")
    return 1


def cmd_summary(args):
    t = load_tprm(args.data)
    reference = _reference(args)
    details = assess_vendors(t)
    crit = sum(1 for d in details if d.residual_level == "Crítico")
    high = sum(1 for d in details if d.residual_level == "Alto")
    openf = [f for f in t.findings if f.status != "Fechado"]
    states = [contract_timing(c, reference)[0] for c in t.contracts]
    print("=" * 68)
    print("THIRD-PARTY RISK ASSESSMENT - MERIDIAN PAY (TPRM)")
    print("=" * 68)
    print(f"Reference date             : {reference.isoformat()}")
    print(f"Vendors                    : {len(t.vendors)}")
    print(f"Assessments                : {len(t.assessments)}")
    print(f"Open findings              : {len(openf)}")
    print(f"Vendors residual C/H       : {crit}/{high}")
    print(
        f"Contracts expired/expiring : {states.count('Vencido')}/"
        f"{states.count('Vencendo')}"
    )
    print("=" * 68)
    return 0


def cmd_vendors(args):
    t = load_tprm(args.data)
    by_id = {v.vendor_id: v for v in t.vendors}
    print("ID     NAME                     TIER    INHERENT    RESIDUAL    COMPL   OWNER                        END")
    print("-" * 112)
    for d in assess_vendors(t):
        vendor = by_id[d.vendor_id]
        pct = f"{d.compliance_pct}%" if d.compliance_pct is not None else "-"
        print(
            f"{d.vendor_id:<7}{d.vendor_name[:23]:<25}{d.tier:<8}"
            f"{d.inherent_level:<12}{d.residual_level:<12}{pct:<8}"
            f"{vendor.owner:<29}{vendor.contract_end}"
        )
    return 0


def cmd_findings(args):
    t = load_tprm(args.data)
    items = [f for f in t.findings if f.status != "Fechado"]
    items = sorted(items, key=lambda x: {"Crítico":4,"Alto":3,"Moderado":2,"Baixo":1}[x.severity], reverse=True)
    print("ID      VENDOR  SEV      CAT                  TARGET      RESPONSIBLE")
    print("-" * 90)
    for f in items:
        print(f"{f.finding_id:<8}{f.vendor_id:<8}{f.severity:<9}{f.category:<21}{f.target_date:<12}{f.responsible}")
    return 0


def cmd_report(args):
    t = load_tprm(args.data)
    out = Path(args.out) / "tprm-report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_report(t, _reference(args)), encoding="utf-8")
    print(f"report written: {out}")
    return 0


def cmd_dashboard(args):
    t = load_tprm(args.data)
    out = Path(args.out) / "tprm-dashboard.html"
    p = write_dashboard(t, out, _reference(args))
    print(f"dashboard written: {p}")
    return 0


def cmd_risk(args):
    t = load_tprm(args.data)
    details = assess_vendors(t)
    rows = concentration(details)
    country_rows = concentration(details, dimension="country")
    out = Path(args.out) / "tprm-risk-assessment.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_risk_markdown(details, rows, country_rows), encoding="utf-8")
    print("VENDOR                  TIER    INHERENT      RESIDUAL      COMPL  C/A")
    print("-" * 82)
    for d in details:
        pct = f"{d.compliance_pct}%" if d.compliance_pct is not None else "-"
        print(
            f"{d.vendor_name[:22]:<24}{d.tier:<8}{d.inherent_level:<14}{d.residual_level:<14}"
            f"{pct:<7}{d.open_critical}/{d.open_high}"
        )
    print("")
    for label, group in (("category", rows), ("country", country_rows)):
        flagged = [r for r in group if r.flagged]
        print(f"concentration alerts ({label}): {len(flagged)}")
        for row in flagged:
            print(f"  - {row.category}: {row.share_pct}% ({row.tier1} Tier 1)")
    print(f"report written: {out}")
    return 0


def cmd_questionnaire(args):
    t = load_tprm(args.data)
    details = assess_vendors(t)
    out = Path(args.out) / "tprm-questionnaire.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_questionnaire_markdown(t, details), encoding="utf-8")
    assessed = sum(1 for d in details if d.assessed)
    print(f"vendors assessed: {assessed}/{len(details)}")
    for d in details:
        pct = f"{d.compliance_pct}%" if d.compliance_pct is not None else "not assessed"
        print(f"  {d.vendor_id} {d.vendor_name[:24]:<26} {pct}")
    print(f"report written: {out}")
    return 0


def cmd_exit_plan(args):
    t = load_tprm(args.data)
    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of!r} (expected YYYY-MM-DD)", file=sys.stderr)
        return 3
    plans = build_exit_plans(t, as_of)
    out = Path(args.out) / "tprm-exit-plans.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_exit_markdown(plans, as_of), encoding="utf-8")
    print("EXIT PLANS (Tier 1)")
    for plan in plans:
        print(
            f"  {plan.vendor_id} {plan.vendor_name[:24]:<26} {plan.overall:<12} "
            f"gaps={len(plan.gaps)} pending={len(plan.pending)}"
        )
    print(f"report written: {out}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="tprm", description="Third-Party Risk Assessment (TPRM)")
    p.add_argument("--data", default=DEFAULT_DATA_DIR)
    p.add_argument("--out", default=DEFAULT_OUT_DIR)
    sp = p.add_subparsers(dest="command", required=True)
    sp.add_parser("validate").set_defaults(func=cmd_validate)
    summary_parser = sp.add_parser("summary")
    summary_parser.add_argument("--as-of", default=None, help="reference date YYYY-MM-DD (default: today)")
    summary_parser.set_defaults(func=cmd_summary)
    sp.add_parser("vendors").set_defaults(func=cmd_vendors)
    sp.add_parser("findings").set_defaults(func=cmd_findings)
    report_parser = sp.add_parser("report")
    report_parser.add_argument("--as-of", default=None, help="reference date YYYY-MM-DD (default: today)")
    report_parser.set_defaults(func=cmd_report)
    dashboard_parser = sp.add_parser("dashboard")
    dashboard_parser.add_argument("--as-of", default=None, help="reference date YYYY-MM-DD (default: today)")
    dashboard_parser.set_defaults(func=cmd_dashboard)
    sp.add_parser("risk", help="inherent x residual risk + concentration").set_defaults(func=cmd_risk)
    sp.add_parser("questionnaire", help="due diligence questionnaire coverage").set_defaults(func=cmd_questionnaire)
    exit_parser = sp.add_parser("exit-plan", help="Tier 1 exit plans")
    exit_parser.add_argument("--as-of", default=None, help="reference date YYYY-MM-DD (default: today)")
    exit_parser.set_defaults(func=cmd_exit_plan)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except DataError as e:
        print(f"data error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
