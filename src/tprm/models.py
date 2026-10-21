"""Models for TPRM."""

from __future__ import annotations

from dataclasses import dataclass


def _s(x): return str(x).strip()


def _i(x, name, rid):
    try:
        return int(str(x).strip())
    except Exception as e:
        raise ValueError(f"{rid}: {name} must be int") from e


@dataclass(frozen=True)
class Vendor:
    vendor_id: str
    vendor_name: str
    category: str
    criticality: str
    tier: str
    data_access: str
    network_access: str
    contract_start: str
    contract_end: str
    onboard_date: str
    owner: str
    status: str
    country: str

    @classmethod
    def from_row(cls, r):
        return cls(
            vendor_id=_s(r["vendor_id"]), vendor_name=_s(r["vendor_name"]), category=_s(r["category"]),
            criticality=_s(r["criticality"]), tier=_s(r["tier"]), data_access=_s(r["data_access"]),
            network_access=_s(r["network_access"]), contract_start=_s(r["contract_start"]),
            contract_end=_s(r["contract_end"]), onboard_date=_s(r["onboard_date"]),
            owner=_s(r["owner"]), status=_s(r["status"]), country=_s(r["country"]),
        )


@dataclass(frozen=True)
class Assessment:
    assessment_id: str
    vendor_id: str
    assessment_date: str
    assessor: str
    framework: str
    questionnaire_version: str
    status: str
    overall_risk: str
    inherent_risk: str
    residual_risk: str
    due_date: str
    next_review: str
    notes: str

    @classmethod
    def from_row(cls, r):
        return cls(
            assessment_id=_s(r["assessment_id"]), vendor_id=_s(r["vendor_id"]),
            assessment_date=_s(r["assessment_date"]), assessor=_s(r["assessor"]),
            framework=_s(r["framework"]), questionnaire_version=_s(r["questionnaire_version"]),
            status=_s(r["status"]), overall_risk=_s(r["overall_risk"]),
            inherent_risk=_s(r["inherent_risk"]), residual_risk=_s(r["residual_risk"]),
            due_date=_s(r["due_date"]), next_review=_s(r["next_review"]), notes=_s(r["notes"]),
        )


@dataclass(frozen=True)
class Finding:
    finding_id: str
    assessment_id: str
    vendor_id: str
    category: str
    finding: str
    likelihood: int
    impact: int
    severity: str
    status: str
    recommended_mitigation: str
    evidence_required: str
    responsible: str
    target_date: str
    mitigated_on: str

    @classmethod
    def from_row(cls, r):
        return cls(
            finding_id=_s(r["finding_id"]), assessment_id=_s(r["assessment_id"]),
            vendor_id=_s(r["vendor_id"]), category=_s(r["category"]),
            finding=_s(r["finding"]), likelihood=_i(r["likelihood"], "likelihood", r["finding_id"]),
            impact=_i(r["impact"], "impact", r["finding_id"]), severity=_s(r["severity"]),
            status=_s(r["status"]), recommended_mitigation=_s(r["recommended_mitigation"]),
            evidence_required=_s(r["evidence_required"]), responsible=_s(r["responsible"]),
            target_date=_s(r["target_date"]), mitigated_on=_s(r.get("mitigated_on", "")),
        )

    @property
    def score(self) -> int:
        return self.likelihood * self.impact


@dataclass(frozen=True)
class Contract:
    contract_id: str
    vendor_id: str
    contract_type: str
    start_date: str
    end_date: str
    auto_renew: str
    notice_period_days: int
    exit_plan_required: str
    security_addendum: str
    dpa_signed: str
    subprocessors_required: str
    owner: str
    status: str

    @classmethod
    def from_row(cls, r):
        return cls(
            contract_id=_s(r["contract_id"]), vendor_id=_s(r["vendor_id"]),
            contract_type=_s(r["contract_type"]), start_date=_s(r["start_date"]),
            end_date=_s(r["end_date"]), auto_renew=_s(r["auto_renew"]),
            notice_period_days=_i(r["notice_period_days"], "notice_period_days", r["contract_id"]),
            exit_plan_required=_s(r["exit_plan_required"]),
            security_addendum=_s(r["security_addendum"]), dpa_signed=_s(r["dpa_signed"]),
            subprocessors_required=_s(r["subprocessors_required"]),
            owner=_s(r["owner"]), status=_s(r["status"]),
        )
