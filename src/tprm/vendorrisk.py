"""Vendor risk assessment, concentration analysis and exit planning.

Three artefacts are produced from the same data:

* **Inherent x residual risk** per vendor (criticality + data reach + network
  reach, reduced by questionnaire compliance and increased by open findings).
* **Concentration analysis** by vendor category (DORA Art. 29 style): where the
  portfolio depends on too few providers.
* **Exit plans** for Tier 1 providers (DORA Art. 28-30): contractual exit
  readiness, not just a boolean column.

All formulas are intentionally transparent so an auditor can recompute them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .loader import TPRMSet
from .models import Contract, QuestionnaireResponse, Vendor
from .scales import (
    RESPONSE_FACTOR,
    RISK_ORDER,
    TIER_WEIGHT,
    inherent_points,
    level_from_points,
    residual_points,
)


@dataclass(frozen=True)
class VendorRiskDetail:
    vendor_id: str
    vendor_name: str
    category: str
    country: str
    tier: str
    criticality: str
    assessed: bool
    compliance_pct: float | None
    inherent_level: str
    residual_level: str
    inherent_score: int
    residual_score: int
    open_critical: int
    open_high: int
    gaps: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ConcentrationRow:
    category: str
    vendors: int
    tier1: int
    weight: int
    share_pct: float
    flagged: bool


@dataclass(frozen=True)
class ChecklistItem:
    label: str
    status: str
    detail: str


@dataclass(frozen=True)
class ExitPlan:
    vendor_id: str
    vendor_name: str
    category: str
    contract_id: str
    end_date: str
    notice_days: int
    overall: str
    checks: tuple[ChecklistItem, ...]

    @property
    def gaps(self) -> list[ChecklistItem]:
        return [c for c in self.checks if c.status == "Gap"]

    @property
    def pending(self) -> list[ChecklistItem]:
        return [c for c in self.checks if c.status == "A confirmar"]


def _factor(response: str) -> float | None:
    value = response.strip()
    if value in ("Nao", "Não", "NAO", "NÃO"):
        return 0.0
    return RESPONSE_FACTOR.get(value, None)


def _compliance(
    responses: list[QuestionnaireResponse], questions_by_id
) -> tuple[float | None, tuple[str, ...]]:
    weighted = 0.0
    total = 0.0
    gaps: list[str] = []
    for response in responses:
        question = questions_by_id.get(response.question_id)
        if question is None:
            continue
        factor = _factor(response.response)
        if factor is None:  # N/A: excluded from the denominator
            continue
        weighted += factor * question.weight
        total += question.weight
        if factor < 1.0:
            gaps.append(
                f"{question.domain} {question.question_id}: {response.response} "
                f"(esperado: {question.expected_evidence})"
            )
    pct = round(weighted / total * 100, 1) if total else None
    return pct, tuple(gaps)


def assess_vendors(t: TPRMSet) -> list[VendorRiskDetail]:
    questions = t.questions_by_id
    responses_by_vendor = t.responses_by_vendor
    findings_by_vendor = t.findings_by_vendor

    details: list[VendorRiskDetail] = []
    for vendor in t.vendors:
        responses = responses_by_vendor.get(vendor.vendor_id, [])
        pct, gaps = _compliance(responses, questions)
        inherent = inherent_points(
            vendor.criticality, vendor.data_access, vendor.network_access
        )
        findings = findings_by_vendor.get(vendor.vendor_id, [])
        open_critical = sum(
            1 for f in findings if f.severity == "Crítico" and f.status != "Fechado"
        )
        open_high = sum(
            1 for f in findings if f.severity == "Alto" and f.status != "Fechado"
        )
        residual = residual_points(inherent, pct, open_critical, open_high)
        details.append(
            VendorRiskDetail(
                vendor_id=vendor.vendor_id,
                vendor_name=vendor.vendor_name,
                category=vendor.category,
                country=vendor.country,
                tier=vendor.tier,
                criticality=vendor.criticality,
                assessed=bool(responses),
                compliance_pct=pct,
                inherent_level=level_from_points(inherent),
                residual_level=level_from_points(residual),
                inherent_score=inherent,
                residual_score=residual,
                open_critical=open_critical,
                open_high=open_high,
                gaps=gaps,
            )
        )
    return sorted(
        details,
        key=lambda d: (
            -RISK_ORDER[d.residual_level],
            -d.inherent_score,
            d.vendor_id,
        ),
    )


def concentration(
    details: list[VendorRiskDetail],
    threshold_pct: float = 25.0,
    dimension: str = "category",
) -> list[ConcentrationRow]:
    """Group risk weight by ``category`` or ``country`` (DORA Art. 29)."""

    groups: dict[str, list[VendorRiskDetail]] = {}
    for detail in details:
        groups.setdefault(getattr(detail, dimension), []).append(detail)

    weights = {
        group: sum(
            TIER_WEIGHT.get(d.tier, 1) * RISK_ORDER.get(d.residual_level, 1)
            for d in members
        )
        for group, members in groups.items()
    }
    total = sum(weights.values()) or 1
    rows = [
        ConcentrationRow(
            category=group,
            vendors=len(members),
            tier1=sum(1 for d in members if d.tier == "Tier 1"),
            weight=weights[group],
            share_pct=round(weights[group] / total * 100, 1),
            flagged=(
                round(weights[group] / total * 100, 1) >= threshold_pct
                or sum(1 for d in members if d.tier == "Tier 1") >= 2
            ),
        )
        for group, members in groups.items()
    ]
    return sorted(rows, key=lambda r: (-r.share_pct, r.category))


def build_exit_plans(
    t: TPRMSet, as_of: date | None = None, renewal_window_days: int = 365
) -> list[ExitPlan]:
    reference = as_of or date.today()
    contracts = t.contracts_by_vendor
    plans: list[ExitPlan] = []

    for vendor in t.vendors:
        if vendor.tier != "Tier 1":
            continue
        contract = contracts.get(vendor.vendor_id)
        if contract is None:
            continue
        checks = _checks(vendor, contract, reference, renewal_window_days)
        if any(c.status == "Gap" for c in checks):
            overall = "Gap"
        else:
            overall = "OK"
        plans.append(
            ExitPlan(
                vendor_id=vendor.vendor_id,
                vendor_name=vendor.vendor_name,
                category=vendor.category,
                contract_id=contract.contract_id,
                end_date=contract.end_date,
                notice_days=contract.notice_period_days,
                overall=overall,
                checks=tuple(checks),
            )
        )
    return sorted(
        plans,
        key=lambda p: ({"Gap": 0, "A confirmar": 1, "OK": 2}[p.overall], p.end_date, p.vendor_id),
    )


def _yes(raw: str) -> bool:
    return raw.strip().lower() in ("true", "sim", "yes", "1")


def _checks(
    vendor: Vendor, contract: Contract, as_of: date, renewal_window_days: int
) -> list[ChecklistItem]:
    try:
        days_to_end = (date.fromisoformat(contract.end_date) - as_of).days
    except ValueError:
        days_to_end = 10_000

    renewal = (
        f"Contrato vence em {days_to_end} dias - abrir revisao."
        if 0 <= days_to_end <= renewal_window_days
        else f"Vencimento em {contract.end_date}."
    )

    return [
        ChecklistItem(
            "Plano de saida exigido em contrato",
            "OK" if _yes(contract.exit_plan_required) else "Gap",
            "Clausula contratual de exit plan."
            if _yes(contract.exit_plan_required)
            else "Incluir clausula de plano de saida no contrato.",
        ),
        ChecklistItem(
            "Addendum de seguranca",
            "OK" if _yes(contract.security_addendum) else "Gap",
            "Addendum assinado."
            if _yes(contract.security_addendum)
            else "Negociar addendum com controles minimos e SLA.",
        ),
        ChecklistItem(
            "DPA assinado",
            "OK" if _yes(contract.dpa_signed) else "Gap",
            "DPA vigente."
            if _yes(contract.dpa_signed)
            else "Assinar DPA com base legal, retencao e subprocessadores.",
        ),
        ChecklistItem(
            "Subprocessadores declarados",
            "OK" if _yes(contract.subprocessors_required) else "Gap",
            "Lista e notificacao de mudanca previstas."
            if _yes(contract.subprocessors_required)
            else "Exigir lista de subprocessadores e notificacao previa.",
        ),
        ChecklistItem(
            "Prazo de aviso >= 60 dias",
            "OK" if contract.notice_period_days >= 60 else "Gap",
            f"{contract.notice_period_days} dias de aviso previo.",
        ),
        ChecklistItem(
            "Janela de renovacao monitorada",
            "Atencao" if 0 <= days_to_end <= renewal_window_days else "OK",
            renewal,
        ),
        ChecklistItem(
            "Retorno e eliminacao de dados",
            "A confirmar",
            "Confirmar formato de exportacao, prazo de eliminacao e certificado.",
        ),
        ChecklistItem(
            "Teste de transicao executado",
            "A confirmar",
            "Executar teste de mesa de saida e registrar RTO/RPO.",
        ),
        ChecklistItem(
            "Responsavel nomeado",
            "OK" if vendor.owner.strip() else "Gap",
            vendor.owner or "Nomear owner do fornecedor.",
        ),
    ]


def build_risk_markdown(
    details: list[VendorRiskDetail],
    rows: list[ConcentrationRow],
    country_rows: list[ConcentrationRow] | None = None,
) -> str:
    lines: list[str] = []
    add = lines.append
    add("# Avaliacao de Risco de Terceiros - Inerente x Residual")
    add("")
    add("**Metodo:** `inerente = criticidade + sensibilidade de dados + alcance de rede` (1-8); "
        "`residual = inerente - floor(compliance/25) + achados_criticos*2 + achados_altos`. "
        "`residual <= inerente` (achados nao aumentam a exposicao inerente).")
    add("")
    add("## 1) Fornecedores")
    add("")
    add("| Fornecedor | Categoria | Pais | Tier | Inerente | Residual | Compliance | Achados C/A | Avaliado |")
    add("|---|---|---|---|---|---|---|---|---|")
    for d in details:
        pct = f"{d.compliance_pct}%" if d.compliance_pct is not None else "-"
        add(
            f"| {d.vendor_name} ({d.vendor_id}) | {d.category} | {d.country} | {d.tier} | "
            f"{d.inherent_level} ({d.inherent_score}) | {d.residual_level} ({d.residual_score}) | "
            f"{pct} | {d.open_critical}/{d.open_high} | {'Sim' if d.assessed else 'Nao'} |"
        )
    add("")
    add("## 2) Concentracao por categoria (DORA Art. 29)")
    add("")
    add("| Categoria | Fornecedores | Tier 1 | Peso | Share | Alerta |")
    add("|---|---|---|---|---|---|")
    for row in rows:
        add(
            f"| {row.category} | {row.vendors} | {row.tier1} | {row.weight} | "
            f"{row.share_pct}% | {'SIM' if row.flagged else '-'} |"
        )
    add("")
    add("> Alerta quando a categoria concentra >= 25% do peso de risco ou possui >= 2 fornecedores Tier 1.")
    add("")
    if country_rows is not None:
        add("## 3) Concentracao por pais (residencia de dados)")
        add("")
        add("| Pais | Fornecedores | Tier 1 | Peso | Share | Alerta |")
        add("|---|---|---|---|---|---|")
        for row in country_rows:
            add(
                f"| {row.category} | {row.vendors} | {row.tier1} | {row.weight} | "
                f"{row.share_pct}% | {'SIM' if row.flagged else '-'} |"
            )
        add("")
        add("> Pais com >= 25% do peso indica dependencia regulatoria/geografica. "
            "Avaliar transferencia internacional (LGPD Art. 33) e plano de contingencia.")
        add("")
    add("## 4) Lacunas de questionario (Tier 1)")
    add("")
    for d in details:
        if d.gaps:
            add(f"### {d.vendor_name} ({d.vendor_id})")
            for gap in d.gaps:
                add(f"- {gap}")
            add("")
    if not any(d.gaps for d in details):
        add("Nenhuma lacuna de questionario registrada.")
        add("")
    return "\n".join(lines)


def build_questionnaire_markdown(t: TPRMSet, details: list[VendorRiskDetail]) -> str:
    by_id = {d.vendor_id: d for d in details}
    lines: list[str] = []
    add = lines.append
    add("# Due Diligence - Questionario de Fornecedores")
    add("")
    add(f"**Perguntas:** {len(t.questionnaire)} | **Respostas registradas:** {len(t.responses)} "
        f"| **Peso total:** {sum(q.weight for q in t.questionnaire)}")
    add("")
    add("## 1) Cobertura")
    add("")
    add("| Fornecedor | Tier | Respondidas | Compliance | Status |")
    add("|---|---|---|---|---|")
    for vendor in t.vendors:
        detail = by_id.get(vendor.vendor_id)
        answered = len(t.responses_by_vendor.get(vendor.vendor_id, []))
        pct = f"{detail.compliance_pct}%" if detail and detail.compliance_pct is not None else "-"
        status = "Avaliado" if answered else "Nao avaliado"
        add(f"| {vendor.vendor_name} ({vendor.vendor_id}) | {vendor.tier} | {answered} | {pct} | {status} |")
    add("")
    add("## 2) Lacunas por fornecedor")
    add("")
    for detail in details:
        if not detail.gaps:
            continue
        add(f"### {detail.vendor_name} ({detail.vendor_id}) - {detail.compliance_pct}%")
        add("")
        for gap in detail.gaps:
            add(f"- {gap}")
        add("")
    if not any(d.gaps for d in details):
        add("Nenhuma lacuna registrada.")
        add("")
    add("## 3) Escala de resposta")
    add("")
    add("- `Sim` = 100% do peso | `Parcial` = 50% | `Nao` = 0% | `N/A` = excluido do denominador.")
    add("- Compliance abaixo de 70% exige plano de acao antes da contratacao/renovacao.")
    add("")
    return "\n".join(lines)


def build_exit_markdown(plans: list[ExitPlan], as_of: date) -> str:
    lines: list[str] = []
    add = lines.append
    add("# Planos de Saida - Fornecedores Tier 1")
    add("")
    add(f"**Data de referencia:** {as_of.isoformat()}  ")
    add("**Base:** DORA Art. 28-30 (risco de terceiros de TIC e estrategias de saida).")
    add("")
    add("## 1) Resumo")
    add("")
    gaps = sum(1 for p in plans if p.overall == "Gap")
    pending = sum(len(p.pending) for p in plans)
    add(f"- Fornecedores Tier 1 com contrato: **{len(plans)}**")
    add(f"- Com gap contratual: **{gaps}** | OK: **{len(plans) - gaps}**")
    add(f"- Itens operacionais a confirmar: **{pending}** (retorno de dados e teste de transicao)")
    add("")
    add("## 2) Checklist por fornecedor")
    add("")
    for plan in plans:
        add(f"### {plan.vendor_name} ({plan.vendor_id}) - {plan.overall}")
        add("")
        add(f"- Contrato: {plan.contract_id} | Vencimento: {plan.end_date} | Aviso: {plan.notice_days} dias")
        add(f"- Pendencias operacionais: {len(plan.pending)}")
        add("")
        add("| Item | Status | Detalhe |")
        add("|---|---|---|")
        for check in plan.checks:
            add(f"| {check.label} | {check.status} | {check.detail} |")
        add("")
    add("## 3) Runbook de saida (7 passos)")
    add("")
    add("1. **Decisao** - registrar motivo, aprovacao do comite e data-alvo.")
    add("2. **Inventario** - dados, integracoes, credenciais e dependencias do fornecedor.")
    add("3. **Transicao** - plano tecnico, responsaveis, RTO/RPO e rollback.")
    add("4. **Dados** - exportacao em formato aberto, eliminacao e certificado de destruicao.")
    add("5. **Acessos** - revogar contas, chaves e certificados; validar ausencia de trafego.")
    add("6. **Teste** - executar teste de mesa ou piloto e registrar evidencias.")
    add("7. **Encerramento** - lições aprendidas, atualizacao do inventario e do registro de riscos.")
    add("")
    return "\n".join(lines)
