"""CLI for TPRM."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .loader import DataError, load_tprm
from .report import build_report
from .dashboard import write_dashboard

DEFAULT_DATA_DIR = "data"
DEFAULT_OUT_DIR = "build"


def cmd_validate(args):
    t = load_tprm(args.data)
    issues = t.validate()
    if not issues:
        print("OK - TPRM data quality checks passed.")
        return 0
    for i, issue in enumerate(issues, 1):
        print(f"{i:>2}. {issue}")
    return 1


def cmd_summary(args):
    t = load_tprm(args.data)
    crit = sum(1 for v in t.vendors if t.vendor_risk(v) == "Crítico")
    high = sum(1 for v in t.vendors if t.vendor_risk(v) == "Alto")
    openf = [f for f in t.findings if f.status != "Fechado"]
    print("=" * 68)
    print("THIRD-PARTY RISK ASSESSMENT - MERIDIAN PAY (TPRM)")
    print("=" * 68)
    print(f"Vendors                    : {len(t.vendors)}")
    print(f"Assessments                : {len(t.assessments)}")
    print(f"Open findings              : {len(openf)}")
    print(f"Vendors (Critical/High)    : {crit}/{high}")
    print(f"Contracts expiring soon    : {sum(1 for c in t.contracts if c.status == 'Vencendo')}")
    print("=" * 68)
    return 0


def cmd_vendors(args):
    t = load_tprm(args.data)
    print("ID   NAME                    CRIT   TIER  RISK     OWNER                        END")
    print("-" * 95)
    for v in sorted(t.vendors, key=lambda x: ({"Crítico":0,"Alto":1,"Moderado":2,"Baixo":3}[t.vendor_risk(x)], x.vendor_id)):
        print(f"{v.vendor_id:<5}{v.vendor_name:<24}{v.criticality:<7}{v.tier:<6}{t.vendor_risk(v):<9}{v.owner:<29}{v.contract_end}")
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
    out.write_text(build_report(t), encoding="utf-8")
    print(f"report written: {out}")
    return 0


def cmd_dashboard(args):
    t = load_tprm(args.data)
    out = Path(args.out) / "tprm-dashboard.html"
    p = write_dashboard(t, out)
    print(f"dashboard written: {p}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="tprm", description="Third-Party Risk Assessment (TPRM)")
    p.add_argument("--data", default=DEFAULT_DATA_DIR)
    p.add_argument("--out", default=DEFAULT_OUT_DIR)
    sp = p.add_subparsers(dest="command", required=True)
    sp.add_parser("validate").set_defaults(func=cmd_validate)
    sp.add_parser("summary").set_defaults(func=cmd_summary)
    sp.add_parser("vendors").set_defaults(func=cmd_vendors)
    sp.add_parser("findings").set_defaults(func=cmd_findings)
    sp.add_parser("report").set_defaults(func=cmd_report)
    sp.add_parser("dashboard").set_defaults(func=cmd_dashboard)
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
