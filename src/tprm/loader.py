"""Loader for TPRM data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .models import Assessment, Contract, Finding, Vendor
from .scales import compute_vendor_risk, risk_rank


class DataError(RuntimeError):
    pass


def _read(path: Path):
    if not path.exists():
        raise DataError(f"not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@dataclass(frozen=True)
class TPRMSet:
    vendors: list[Vendor]
    assessments: list[Assessment]
    findings: list[Finding]
    contracts: list[Contract]

    @property
    def findings_by_vendor(self):
        out = {}
        for f in self.findings:
            out.setdefault(f.vendor_id, []).append(f)
        return out

    def vendor_risk(self, vendor: Vendor) -> str:
        findings = self.findings_by_vendor.get(vendor.vendor_id, [])
        crit = sum(1 for f in findings if f.severity == "Crítico" and f.status != "Fechado")
        high = sum(1 for f in findings if f.severity == "Alto" and f.status != "Fechado")
        return compute_vendor_risk(vendor.criticality, crit, high)

    def validate(self):
        issues = []
        vids = {v.vendor_id for v in self.vendors}
        aids = {a.assessment_id for a in self.assessments}
        for f in self.findings:
            if f.vendor_id not in vids:
                issues.append(f"{f.finding_id}: unknown vendor {f.vendor_id}")
            if f.assessment_id not in aids:
                issues.append(f"{f.finding_id}: unknown assessment {f.assessment_id}")
        for c in self.contracts:
            if c.vendor_id not in vids:
                issues.append(f"{c.contract_id}: unknown vendor {c.vendor_id}")
        return issues


def load_tprm(data_dir: str | Path) -> TPRMSet:
    base = Path(data_dir)
    return TPRMSet(
        vendors=[Vendor.from_row(r) for r in _read(base / "vendors.csv")],
        assessments=[Assessment.from_row(r) for r in _read(base / "assessments.csv")],
        findings=[Finding.from_row(r) for r in _read(base / "findings.csv")],
        contracts=[Contract.from_row(r) for r in _read(base / "contracts.csv")],
    )
