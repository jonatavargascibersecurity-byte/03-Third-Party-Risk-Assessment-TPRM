"""TPRM static HTML dashboard.

The dashboard reads the same inherent/residual model as ``tprm risk`` so the
cards, the report and the CLI summary always agree.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

from .loader import TPRMSet
from .vendorrisk import assess_vendors, concentration, contract_timing

CSS = """
:root{--bg:#f4f6f8;--card:#fff;--ink:#1b2430;--muted:#5c6b7a;--line:#dfe5ec}
*{box-sizing:border-box}body{margin:0;font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
header{background:linear-gradient(135deg,#0b1b3a,#0b5fff);color:#fff;padding:28px 32px}
header h1{margin:0 0 6px}header p{margin:0;opacity:.85}
main{padding:24px 32px 48px;max-width:1180px;margin:0 auto}
h2{margin:32px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.cards{display:flex;flex-wrap:wrap;gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;min-width:180px;flex:1}
.card .label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.card .value{font-size:28px;font-weight:700;margin-top:6px}
.card .sub{font-size:12px;color:var(--muted);margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:9px 12px;text-align:left;font-size:13px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#eef2f7;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
tr:last-child td{border-bottom:none}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:700;color:#fff}
.muted{color:var(--muted)}
footer{color:var(--muted);font-size:12px;margin-top:32px;border-top:1px solid var(--line);padding-top:12px}
"""

SEV_COLOR = {
    "Crítico": "#c62828",
    "Alto": "#ef6c00",
    "Moderado": "#f9a825",
    "Baixo": "#2e7d32",
}
STATE_COLOR = {"Vencido": "#c62828", "Vencendo": "#ef6c00", "Ativo": "#2e7d32"}


def _esc(x):
    return escape(str(x), quote=True)


def _pill(text, color="#5c6b7a"):
    return f"<span class='pill' style='background:{color}'>{_esc(text)}</span>"


def build_dashboard(
    t: TPRMSet,
    generated_at: datetime | None = None,
    as_of: date | None = None,
) -> str:
    now = generated_at or datetime.now(timezone.utc)
    reference = as_of or date.today()
    details = assess_vendors(t)
    contracts = t.contracts_by_vendor
    states = {
        contract.contract_id: contract_timing(contract, reference)
        for contract in t.contracts
    }
    openf = [f for f in t.findings if f.status != "Fechado"]
    crit = sum(1 for d in details if d.residual_level == "Crítico")
    high = sum(1 for d in details if d.residual_level == "Alto")
    expired = sum(1 for state, _ in states.values() if state == "Vencido")
    expiring = sum(1 for state, _ in states.values() if state == "Vencendo")

    html = []
    add = html.append
    add(
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    )
    add("<title>TPRM Dashboard - Meridian Pay</title>")
    add(f"<style>{CSS}</style></head><body>")
    add("<header><h1>Third-Party Risk Assessment (TPRM) - Meridian Pay</h1>")
    add(
        f"<p>Fictional Brazilian fintech &#183; generated "
        f"{now.strftime('%Y-%m-%d %H:%M UTC')} &#183; reference {reference.isoformat()}</p>"
        "</header>"
    )
    add("<main>")
    add("<div class='cards'>")
    add(
        f"<div class='card'><div class='label'>Vendors</div>"
        f"<div class='value'>{len(t.vendors)}</div>"
        f"<div class='sub'>{crit} Critical / {high} High (residual)</div></div>"
    )
    add(
        f"<div class='card'><div class='label'>Assessments</div>"
        f"<div class='value'>{len(t.assessments)}</div>"
        f"<div class='sub'>due diligence</div></div>"
    )
    add(
        f"<div class='card'><div class='label'>Open findings</div>"
        f"<div class='value'>{len(openf)}</div>"
        f"<div class='sub'>{sum(1 for f in openf if f.severity == 'Crítico')} Critical</div></div>"
    )
    add(
        f"<div class='card'><div class='label'>Contract dates</div>"
        f"<div class='value'>{expired + expiring}</div>"
        f"<div class='sub'>{expired} expired / {expiring} expiring</div></div>"
    )
    add("</div>")
    add(
        "<h2>Vendor Risk Register - Inherent x Residual</h2><table><thead><tr>"
        "<th>ID</th><th>Vendor</th><th>Tier</th><th>Inherent</th><th>Residual</th>"
        "<th>Compliance</th><th>Open C/H</th><th>Contract end</th><th>Contract state</th>"
        "</tr></thead><tbody>"
    )
    for detail in details:
        contract = contracts.get(detail.vendor_id)
        if contract is None:
            end_date, state, days = "-", "-", 0
        else:
            end_date = contract.end_date
            state, days = states[contract.contract_id]
        state_text = f"{state} ({abs(days)}d)" if state in ("Vencido", "Vencendo") else state
        pct = f"{detail.compliance_pct}%" if detail.compliance_pct is not None else "n/a"
        add(
            f"<tr><td>{_esc(detail.vendor_id)}</td><td>{_esc(detail.vendor_name)}</td>"
            f"<td>{_esc(detail.tier)}</td>"
            f"<td>{_pill(detail.inherent_level, SEV_COLOR[detail.inherent_level])} "
            f"({detail.inherent_score})</td>"
            f"<td>{_pill(detail.residual_level, SEV_COLOR[detail.residual_level])} "
            f"({detail.residual_score})</td>"
            f"<td>{_esc(pct)}</td>"
            f"<td>{detail.open_critical}/{detail.open_high}</td>"
            f"<td class='muted'>{_esc(end_date)}</td>"
            f"<td>{_pill(state_text, STATE_COLOR.get(state, '#5c6b7a'))}</td></tr>"
        )
    add("</tbody></table>")
    add(
        "<h2>Concentration by Country - DORA Art. 29</h2><table><thead><tr>"
        "<th>Country</th><th>Vendors</th><th>Tier 1</th><th>Risk weight</th>"
        "<th>Share</th><th>Alert</th></tr></thead><tbody>"
    )
    for row in concentration(details, dimension="country"):
        alert = _pill("ALERTA", "#c62828") if row.flagged else "-"
        add(
            f"<tr><td>{_esc(row.category)}</td><td>{row.vendors}</td>"
            f"<td>{row.tier1}</td><td>{row.weight}</td>"
            f"<td>{row.share_pct}%</td><td>{alert}</td></tr>"
        )
    add("</tbody></table>")
    add(
        "<h2>Open Findings</h2><table><thead><tr><th>ID</th><th>Vendor</th>"
        "<th>Severity</th><th>Category</th><th>Mitigation</th><th>Target</th>"
        "</tr></thead><tbody>"
    )
    for finding in sorted(
        openf,
        key=lambda x: {"Crítico": 4, "Alto": 3, "Moderado": 2, "Baixo": 1}[x.severity],
        reverse=True,
    ):
        add(
            f"<tr><td>{_esc(finding.finding_id)}</td><td>{_esc(finding.vendor_id)}</td>"
            f"<td>{_pill(finding.severity, SEV_COLOR[finding.severity])}</td>"
            f"<td>{_esc(finding.category)}</td>"
            f"<td>{_esc(finding.recommended_mitigation)}</td>"
            f"<td class='muted'>{_esc(finding.target_date)}</td></tr>"
        )
    add("</tbody></table>")
    add(
        "<footer>Generated by <span class='mono'>python -m tprm dashboard</span> "
        "&#183; inherent/residual model shared with <span class='mono'>tprm risk</span> "
        "&#183; portfolio project, fictional scenario.</footer>"
    )
    add("</main></body></html>")
    return "\n".join(html)


def write_dashboard(
    t: TPRMSet, out: str | Path, as_of: date | None = None
) -> Path:
    p = Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(build_dashboard(t, as_of=as_of), encoding="utf-8")
    return p
