"""TPRM executive report."""

from __future__ import annotations

from datetime import datetime, timezone

from .loader import TPRMSet
from .scales import RISK_LEVEL_EN

COMPANY = "Meridian Pay"


def build_report(t: TPRMSet) -> str:
    now = datetime.now(timezone.utc)
    lines = []
    add = lines.append
    add(f"# Third-Party Risk Assessment (TPRM) Report - {COMPANY}")
    add("")
    add("> Fictional Brazilian fintech used as portfolio scenario.")
    add("")
    add(f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}")
    add("")
    add("## 1) Portfolio overview")
    add("")
    add(f"- **Vendors:** {len(t.vendors)}")
    add(f"- **Assessments:** {len(t.assessments)}")
    add(f"- **Open findings:** {sum(1 for f in t.findings if f.status != 'Fechado')}")
    add(f"- **Contracts expiring:** {sum(1 for c in t.contracts if c.status == 'Vencendo')}")
    add("")
    add("## 2) Vendor risk register")
    add("")
    add("| Vendor | Category | Criticality | Tier | Vendor risk | Contract end |")
    add("|---|---|---|---|---|---|")
    for v in sorted(t.vendors, key=lambda x: {"Crítico":0,"Alto":1,"Moderado":2,"Baixo":3}[t.vendor_risk(x)]):
        add(f"| {v.vendor_name} | {v.category} | {v.criticality} | {v.tier} | {t.vendor_risk(v)} | {v.contract_end} |")
    add("")
    add("## 3) Open findings (by severity)")
    add("")
    add("| Finding | Vendor | Severity | Category | Mitigation | Target | Responsible |")
    add("|---|---|---|---|---|---|---|")
    for f in sorted([f for f in t.findings if f.status != "Fechado"], key=lambda x: {"Crítico":4,"Alto":3,"Moderado":2,"Baixo":1}[x.severity], reverse=True):
        add(f"| {f.finding_id} | {f.vendor_id} | {f.severity} | {f.category} | {f.recommended_mitigation} | {f.target_date} | {f.responsible} |")
    add("")
    add("## 4) Contract risk")
    add("")
    add("| Contract | Vendor | End date | Notice | Exit plan | Security addendum | DPA |")
    add("|---|---|---|---|---|---|---|")
    for c in t.contracts:
        add(f"| {c.contract_id} | {c.vendor_id} | {c.end_date} | {c.notice_period_days}d | {c.exit_plan_required} | {c.security_addendum} | {c.dpa_signed} |")
    add("")
    add("## 5) Methodology")
    add("")
    add("- **Tiering**: Tier 1 (critical, data/network privileged), Tier 2 (high), Tier 3 (low).")
    add("- **Vendor risk**: criticality plus open Critical/High findings (weighted).")
    add("- **Due diligence**: questionnaire + evidence + contract clauses (security addendum, DPA, subprocessors).")
    add("- **Continuous monitoring**: reassessment cadence and contract expiry tracking.")
    add("")
    return "\n".join(lines)
