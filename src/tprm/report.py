"""TPRM executive report.

The report uses the same inherent/residual model as ``tprm risk`` and the
dashboard. The legacy criticality-plus-findings score is *not* used here, so a
vendor can never show one severity in the summary and another in the assessment.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from .loader import TPRMSet
from .vendorrisk import assess_vendors, concentration, contract_timing

COMPANY = "Meridian Pay"


def _pct(value: float | None) -> str:
    return f"{value}%" if value is not None else "n/a"


def build_report(t: TPRMSet, as_of: date | None = None) -> str:
    now = datetime.now(timezone.utc)
    reference = as_of or date.today()
    details = assess_vendors(t)
    contracts = t.contracts_by_vendor
    critical = sum(1 for d in details if d.residual_level == "Crítico")
    high = sum(1 for d in details if d.residual_level == "Alto")
    open_findings = [f for f in t.findings if f.status != "Fechado"]
    states = {
        contract.contract_id: contract_timing(contract, reference)
        for contract in t.contracts
    }
    expired = sum(1 for state, _ in states.values() if state == "Vencido")
    expiring = sum(1 for state, _ in states.values() if state == "Vencendo")

    lines = []
    add = lines.append
    add(f"# Third-Party Risk Assessment (TPRM) Report - {COMPANY}")
    add("")
    add("> Fictional Brazilian fintech used as portfolio scenario.")
    add("")
    add(
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')} | "
        f"**Reference date:** {reference.isoformat()}"
    )
    add("")
    add("## 1) Portfolio overview")
    add("")
    add(f"- **Vendors:** {len(t.vendors)}")
    add(f"- **Assessments:** {len(t.assessments)}")
    add(f"- **Open findings:** {len(open_findings)}")
    add(f"- **Residual risk (Critical/High):** {critical}/{high}")
    add(f"- **Contracts expired:** {expired} | **Expiring in 90 days:** {expiring}")
    add("")
    add("## 2) Vendor risk register (inherent x residual)")
    add("")
    add(
        "| Vendor | Category | Tier | Inherent | Residual | Compliance | Open C/H | "
        "Contract end | Contract state |"
    )
    add("|---|---|---|---|---|---|---|---|---|")
    for detail in details:
        contract = contracts.get(detail.vendor_id)
        if contract is None:
            end_date, state = "-", "-"
        else:
            end_date = contract.end_date
            state, days = states[contract.contract_id]
            if state == "Vencido":
                state = f"{state} ({abs(days)}d)"
            elif state == "Vencendo":
                state = f"{state} ({days}d)"
        add(
            f"| {detail.vendor_name} | {detail.category} | {detail.tier} | "
            f"{detail.inherent_level} ({detail.inherent_score}) | "
            f"{detail.residual_level} ({detail.residual_score}) | "
            f"{_pct(detail.compliance_pct)} | "
            f"{detail.open_critical}/{detail.open_high} | {end_date} | {state} |"
        )
    add("")
    add("## 3) Open findings (by severity)")
    add("")
    add(
        "| Finding | Vendor | Severity | Category | Mitigation | Target | Responsible |"
    )
    add("|---|---|---|---|---|---|---|")
    for finding in sorted(
        open_findings,
        key=lambda x: {"Crítico": 4, "Alto": 3, "Moderado": 2, "Baixo": 1}[x.severity],
        reverse=True,
    ):
        add(
            f"| {finding.finding_id} | {finding.vendor_id} | {finding.severity} | "
            f"{finding.category} | {finding.recommended_mitigation} | "
            f"{finding.target_date} | {finding.responsible} |"
        )
    add("")
    add("## 4) Contract risk")
    add("")
    add(
        "| Contract | Vendor | End date | State | Notice | Exit plan | Security addendum | DPA |"
    )
    add("|---|---|---|---|---|---|---|---|")
    for contract in t.contracts:
        state, days = states[contract.contract_id]
        if state == "Vencido":
            state = f"{state} ({abs(days)}d)"
        elif state == "Vencendo":
            state = f"{state} ({days}d)"
        add(
            f"| {contract.contract_id} | {contract.vendor_id} | {contract.end_date} | "
            f"{state} | {contract.notice_period_days}d | {contract.exit_plan_required} | "
            f"{contract.security_addendum} | {contract.dpa_signed} |"
        )
    add("")
    add("## 5) Concentration risk (DORA Art. 29)")
    add("")
    add("| Country | Vendors | Tier 1 | Risk weight | Share | Alert |")
    add("|---|---|---|---|---|---|")
    for row in concentration(details, dimension="country"):
        add(
            f"| {row.category} | {row.vendors} | {row.tier1} | {row.weight} | "
            f"{row.share_pct}% | {'SIM' if row.flagged else '-'} |"
        )
    add("")
    add("## 6) Methodology")
    add("")
    add(
        "- **Inherent** = criticality (1-4) + data sensitivity (0-2) + network reach (0-2)."
    )
    add(
        "- **Residual** = inherent - floor(questionnaire compliance / 25) + "
        "open Critical x2 + open High; capped at the inherent score."
    )
    add(
        "- **Unassessed vendors** keep residual = inherent (conservative: no due "
        "diligence evidence, no control credit)."
    )
    add(
        "- **Contracts** are classified by date (`Vencido` / `Vencendo` / `Ativo`), "
        "not by a stale manual status."
    )
    add(
        "- **Tiering**: Tier 1 (critical, data/network privileged), Tier 2 (high), "
        "Tier 3 (low)."
    )
    add("")
    return "\n".join(lines)
