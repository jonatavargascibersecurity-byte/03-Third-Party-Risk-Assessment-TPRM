"""Scales for TPRM."""

from __future__ import annotations

CRITICALITY = ("Crítico", "Alto", "Moderado", "Baixo")
TIER = ("Tier 1", "Tier 2", "Tier 3")
RISK_LEVEL = ("Crítico", "Alto", "Moderado", "Baixo")
STATUS = ("Ativo", "Em avaliação", "Suspenso", "Encerrado")
RISK_LEVEL_EN = {"Crítico": "Critical", "Alto": "High", "Moderado": "Moderate", "Baixo": "Low"}
RISK_ORDER = {"Crítico": 4, "Alto": 3, "Moderado": 2, "Baixo": 1}


def risk_rank(r: str) -> int:
    return RISK_ORDER.get(r, 0)


def compute_vendor_risk(criticality: str, findings_crit: int, findings_high: int) -> str:
    score = RISK_ORDER.get(criticality, 1)
    score += findings_crit * 2
    score += findings_high * 1
    if score >= 8:
        return "Crítico"
    if score >= 4:
        return "Alto"
    if score >= 2:
        return "Moderado"
    return "Baixo"


# --- Inherent / residual model ---------------------------------------------
# Points are an indicative 1-8 scale: criticality (1-4) + data sensitivity
# (0-2) + network reach (0-2). The questionnaire then removes up to 4 points.
# It is deliberately simple and auditable, not a quantified FAIR model.

TIER_WEIGHT = {"Tier 1": 3, "Tier 2": 2, "Tier 3": 1}

RESPONSE_FACTOR = {"Sim": 1.0, "Parcial": 0.5, "Nao": 0.0, "N/A": None}


def data_points(access: str) -> int:
    value = (access or "").lower()
    if any(k in value for k in ("privilegiado", "biometric", "pii", "repositorio", "logs de seguranca")):
        return 2
    if "sem acesso" in value:
        return 0
    return 1


def network_points(access: str) -> int:
    value = (access or "").lower()
    if any(k in value for k in ("privilegiado", "sistema critico", "ambiente log")):
        return 2
    if "sem acesso" in value:
        return 0
    return 1


def level_from_points(points: int) -> str:
    if points >= 7:
        return "Crítico"
    if points >= 5:
        return "Alto"
    if points >= 3:
        return "Moderado"
    return "Baixo"


def inherent_points(criticality: str, data_access: str, network_access: str) -> int:
    return (
        RISK_ORDER.get(criticality, 1)
        + data_points(data_access)
        + network_points(network_access)
    )


def residual_points(inherent: int, compliance_pct: float | None, critical_open: int, high_open: int) -> int:
    reduction = 0 if compliance_pct is None else int(compliance_pct // 25)
    points = inherent - reduction + critical_open * 2 + high_open
    # Residual can never exceed inherent: findings erode the control benefit,
    # they do not create new inherent exposure.
    return max(1, min(inherent, points))
