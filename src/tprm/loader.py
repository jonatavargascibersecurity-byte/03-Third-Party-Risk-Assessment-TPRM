"""Loader for TPRM data."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from .models import (
    Assessment,
    Contract,
    Finding,
    QuestionnaireQuestion,
    QuestionnaireResponse,
    Vendor,
)
from .scales import compute_vendor_risk, risk_rank


class DataError(RuntimeError):
    pass


def _read(path: Path):
    if not path.exists():
        raise DataError(f"not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for line, row in enumerate(rows, start=2):
            if None in row:
                raise DataError(
                    f"{path}:{line}: extra column(s) - row has more values than the header"
                )
        return rows


@dataclass(frozen=True)
class TPRMSet:
    vendors: list[Vendor]
    assessments: list[Assessment]
    findings: list[Finding]
    contracts: list[Contract]
    questionnaire: list[QuestionnaireQuestion] = field(default_factory=list)
    responses: list[QuestionnaireResponse] = field(default_factory=list)

    @property
    def findings_by_vendor(self):
        out = {}
        for f in self.findings:
            out.setdefault(f.vendor_id, []).append(f)
        return out

    @property
    def contracts_by_vendor(self):
        out = {}
        for c in self.contracts:
            out.setdefault(c.vendor_id, c)
        return out

    @property
    def responses_by_vendor(self):
        out = {}
        for r in self.responses:
            out.setdefault(r.vendor_id, []).append(r)
        return out

    @property
    def questions_by_id(self):
        return {q.question_id: q for q in self.questionnaire}

    def vendor_risk(self, vendor: Vendor) -> str:
        """Legacy criticality + open-findings score.

        Kept for compatibility with older callers/tests. Reports, dashboards,
        summaries and ``vendors`` use the canonical inherent/residual model in
        :func:`tprm.vendorrisk.assess_vendors` instead.
        """

        findings = self.findings_by_vendor.get(vendor.vendor_id, [])
        crit = sum(1 for f in findings if f.severity == "Crítico" and f.status != "Fechado")
        high = sum(1 for f in findings if f.severity == "Alto" and f.status != "Fechado")
        return compute_vendor_risk(vendor.criticality, crit, high)

    def validate(self):
        issues = []
        from datetime import date

        from .scales import CRITICALITY, TIER, RISK_LEVEL

        vids = {v.vendor_id for v in self.vendors}
        aids = {a.assessment_id for a in self.assessments}
        qids = {q.question_id for q in self.questionnaire}

        seen_vendors = set()
        for v in self.vendors:
            if v.vendor_id in seen_vendors:
                issues.append(f"{v.vendor_id}: duplicated vendor_id")
            seen_vendors.add(v.vendor_id)
            if v.criticality not in CRITICALITY:
                issues.append(f"{v.vendor_id}: unknown criticality '{v.criticality}'")
            if v.tier not in TIER:
                issues.append(f"{v.vendor_id}: unknown tier '{v.tier}'")
            if v.status not in ("Ativo", "Em avaliação", "Suspenso", "Encerrado"):
                issues.append(f"{v.vendor_id}: unknown status '{v.status}'")
            for field in ("contract_start", "contract_end", "onboard_date"):
                try:
                    date.fromisoformat(getattr(v, field))
                except ValueError:
                    issues.append(f"{v.vendor_id}: {field} must be YYYY-MM-DD")

        seen_assessments = set()
        for a in self.assessments:
            if a.assessment_id in seen_assessments:
                issues.append(f"{a.assessment_id}: duplicated assessment_id")
            seen_assessments.add(a.assessment_id)
            if a.vendor_id not in vids:
                issues.append(f"{a.assessment_id}: unknown vendor {a.vendor_id}")
            if a.status not in ("Concluído", "Em andamento"):
                issues.append(f"{a.assessment_id}: unknown status '{a.status}'")
            for risk_field in ("overall_risk", "inherent_risk", "residual_risk"):
                if getattr(a, risk_field) not in RISK_LEVEL:
                    issues.append(
                        f"{a.assessment_id}: unknown {risk_field} "
                        f"'{getattr(a, risk_field)}'"
                    )
            for field in ("assessment_date", "due_date", "next_review"):
                try:
                    date.fromisoformat(getattr(a, field))
                except ValueError:
                    issues.append(f"{a.assessment_id}: {field} must be YYYY-MM-DD")

        seen_findings = set()
        for f in self.findings:
            if f.finding_id in seen_findings:
                issues.append(f"{f.finding_id}: duplicated finding_id")
            seen_findings.add(f.finding_id)
            if f.vendor_id not in vids:
                issues.append(f"{f.finding_id}: unknown vendor {f.vendor_id}")
            if f.assessment_id not in aids:
                issues.append(f"{f.finding_id}: unknown assessment {f.assessment_id}")
            if f.severity not in RISK_LEVEL:
                issues.append(f"{f.finding_id}: unknown severity '{f.severity}'")
            if f.status not in ("Aberto", "Em aberto", "Em tratamento", "Fechado"):
                issues.append(f"{f.finding_id}: unknown status '{f.status}'")
            if not 1 <= f.likelihood <= 5 or not 1 <= f.impact <= 5:
                issues.append(f"{f.finding_id}: likelihood/impact must be 1-5")
            try:
                date.fromisoformat(f.target_date)
            except ValueError:
                issues.append(f"{f.finding_id}: target_date must be YYYY-MM-DD")

        seen_contracts = set()
        contracts_per_vendor: dict[str, str] = {}
        for c in self.contracts:
            if c.contract_id in seen_contracts:
                issues.append(f"{c.contract_id}: duplicated contract_id")
            seen_contracts.add(c.contract_id)
            if c.vendor_id not in vids:
                issues.append(f"{c.contract_id}: unknown vendor {c.vendor_id}")
            if c.vendor_id in contracts_per_vendor:
                issues.append(
                    f"{c.contract_id}: vendor {c.vendor_id} already has contract "
                    f"{contracts_per_vendor[c.vendor_id]} (one contract per vendor)"
                )
            else:
                contracts_per_vendor[c.vendor_id] = c.contract_id
            vendor = next((v for v in self.vendors if v.vendor_id == c.vendor_id), None)
            if vendor is not None and (
                vendor.contract_start != c.start_date
                or vendor.contract_end != c.end_date
            ):
                issues.append(
                    f"{c.contract_id}: dates diverge from vendor "
                    f"{vendor.vendor_id} ({vendor.contract_start}..{vendor.contract_end} "
                    f"vs {c.start_date}..{c.end_date})"
                )
            if c.status not in ("Ativo", "Vencendo", "Encerrado", "Vencido"):
                issues.append(f"{c.contract_id}: unknown status '{c.status}'")
            try:
                start = date.fromisoformat(c.start_date)
                end = date.fromisoformat(c.end_date)
            except ValueError:
                issues.append(f"{c.contract_id}: start_date/end_date must be YYYY-MM-DD")
            else:
                if end < start:
                    issues.append(f"{c.contract_id}: end_date before start_date")
            if c.notice_period_days < 0:
                issues.append(f"{c.contract_id}: notice_period_days must be >= 0")

        seen_questions: set[str] = set()
        for q in self.questionnaire:
            if q.question_id in seen_questions:
                issues.append(f"{q.question_id}: duplicated question_id")
            seen_questions.add(q.question_id)
            if q.weight < 1:
                issues.append(f"{q.question_id}: weight must be >= 1")

        seen_responses = set()
        for r in self.responses:
            key = (r.vendor_id, r.question_id)
            if key in seen_responses:
                issues.append(f"resp {r.vendor_id}/{r.question_id}: duplicated response")
            seen_responses.add(key)
            if r.vendor_id not in vids:
                issues.append(f"resp {r.vendor_id}/{r.question_id}: unknown vendor {r.vendor_id}")
            if r.question_id not in qids:
                issues.append(f"resp {r.vendor_id}/{r.question_id}: unknown question {r.question_id}")
            if r.response not in ("Sim", "Parcial", "Nao", "Não", "N/A", "NA"):
                issues.append(f"resp {r.vendor_id}/{r.question_id}: unknown response '{r.response}'")
            try:
                date.fromisoformat(r.assessed_on)
            except ValueError:
                issues.append(f"resp {r.vendor_id}/{r.question_id}: assessed_on must be YYYY-MM-DD")
        return issues


def load_tprm(data_dir: str | Path) -> TPRMSet:
    base = Path(data_dir)

    def optional(name):
        path = base / name
        return list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline=""))) if path.exists() else []

    return TPRMSet(
        vendors=[Vendor.from_row(r) for r in _read(base / "vendors.csv")],
        assessments=[Assessment.from_row(r) for r in _read(base / "assessments.csv")],
        findings=[Finding.from_row(r) for r in _read(base / "findings.csv")],
        contracts=[Contract.from_row(r) for r in _read(base / "contracts.csv")],
        questionnaire=[QuestionnaireQuestion.from_row(r) for r in optional("questionnaire.csv")],
        responses=[QuestionnaireResponse.from_row(r) for r in optional("questionnaire_responses.csv")],
    )
