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
