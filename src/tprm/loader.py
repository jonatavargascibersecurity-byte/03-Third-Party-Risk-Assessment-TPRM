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
        findings = self.findings_by_vendor.get(vendor.vendor_id, [])
        crit = sum(1 for f in findings if f.severity == "Crítico" and f.status != "Fechado")
        high = sum(1 for f in findings if f.severity == "Alto" and f.status != "Fechado")
        return compute_vendor_risk(vendor.criticality, crit, high)

    def validate(self):
        issues = []
        vids = {v.vendor_id for v in self.vendors}
        aids = {a.assessment_id for a in self.assessments}
        qids = {q.question_id for q in self.questionnaire}
        for f in self.findings:
            if f.vendor_id not in vids:
                issues.append(f"{f.finding_id}: unknown vendor {f.vendor_id}")
            if f.assessment_id not in aids:
                issues.append(f"{f.finding_id}: unknown assessment {f.assessment_id}")
        for c in self.contracts:
            if c.vendor_id not in vids:
                issues.append(f"{c.contract_id}: unknown vendor {c.vendor_id}")
        for r in self.responses:
            if r.vendor_id not in vids:
                issues.append(f"resp {r.vendor_id}/{r.question_id}: unknown vendor {r.vendor_id}")
            if r.question_id not in qids:
                issues.append(f"resp {r.vendor_id}/{r.question_id}: unknown question {r.question_id}")
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
