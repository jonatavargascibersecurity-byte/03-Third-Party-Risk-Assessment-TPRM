# Plataformas, conteúdo real e como este repositório se conecta

Este repositório referencia **conteúdo específico e verificável** de TryHackMe, LetsDefend e Hack The Box Academy — sala, curso ou módulo, com link direto. Não usamos link para a home da plataforma nem para uma trilha genérica.

**Verificado em:** 2026-11-03.

## Mapeamento direto

| Plataforma / conteúdo | Link | Seções/tasks reais | O que foi aplicado no repositório | Evidência rastreável |
|---|---|---|---|---|
| **TryHackMe — Governance & Regulation** (sala) | https://tryhackme.com/room/cybergovernanceregulation | Task 4: Governance Risk and Compliance (GRC); Task 5: Privacy and Data Protection; Task 6: NIST Special Publications; Task 7: Information Security Management and Compliance (ISO/IEC 27001 e SOC 2) | Perguntas de due diligence sobre DPA/LGPD, subprocessadores e cláusula de auditoria; campos contratuais `dpa_signed`, `security_addendum` e `subprocessors_required` | `data/questionnaire.csv` (Q05, Q07, Q08), `data/contracts.csv` e `python -m tprm questionnaire` |
| **TryHackMe — Risk Management** (sala) | https://tryhackme.com/room/seriskmanagement | Basic Terminology; Risk Assessment; Risk Management Process (Frame → Assess → Respond → Monitor); risco de supply chain no monitoramento | Modelo inerente/residual por fornecedor, resposta a risco via plano de saída e monitoramento por concentração e prazo contratual | `src/tprm/vendorrisk.py` (`inherent_points`, `residual_points`, `concentration`, `contract_timing`) e `python -m tprm --out build risk` |
| **LetsDefend — Risk Management** (curso) | https://app.letsdefend.io/training/lessons/risk-management | Introduction to Risk Management; Risk Management Terminology; Risk Management Framework; Risk Assessment Step By Step; Risk Calculation Issue; Quantitative vs Qualitative Risk Calculation | Escala 0-10, níveis Crítico/Alto/Moderado/Baixo, crédito do questionário e regra `residual <= inerente` | `src/tprm/scales.py`, `assess_vendors` e `python -m tprm validate` |
| **LetsDefend — Security Product Selection** (SOC Manager) | https://app.letsdefend.io/training/lessons/security-product-selection | Organizational Needs and Budget Constraints; Comparative Analysis of Security Products; Decision-Making Strategies in Product Selection | Tiering/criticidade do fornecedor, questionário ponderado (pesos 1-3) e cobertura de due diligence | `data/vendors.csv`, `data/questionnaire.csv`, `data/questionnaire_responses.csv` e `python -m tprm --out build questionnaire` |
| **HTB Academy — Supply Chain Attacks** (módulo) | https://academy.hackthebox.com/course/preview/supply-chain-attacks | Introduction to Supply Chains; Lifecycle of a Supply Chain Attack; Hardware/Software Supply Chain Attacks; Common Attack Vectors; The SolarWinds Attack; Insider Threats; Skills Assessment | Exigência de lista de subprocessadores, plano de saída para Tier 1 e concentração por categoria/país (DORA Art. 28-29) | `data/contracts.csv` (`subprocessors_required`), `python -m tprm --out build exit-plan --as-of 2026-11-02` e `python -m tprm --out build risk` |

## Por que esses links são os reais

- **TryHackMe:** os links abrem a sala diretamente (`/room/<slug>`), não o módulo. A sala *Governance & Regulation* é a que cobre GRC, ISO/IEC 27001, SOC 2 e privacidade; a sala *Risk Management* é a que cobre Frame → Assess → Respond → Monitor e supply chain risk.
- **LetsDefend:** os links abrem a lição/curso (`/training/lessons/<slug>`). *Risk Management* traz cálculo quantitativo vs qualitativo; *Security Product Selection* traz comparação estruturada de fornecedores.
- **HTB Academy:** o link abre o módulo (`/course/preview/<slug>`), com as seções de supply chain, SolarWinds e insider threats.
- O TryHackMe pode responder **HTTP 429** para requisições automatizadas (rate limit); isso não invalida a sala. Os títulos e conteúdos foram conferidos em 2026-11-03.

O detalhamento do que cada conteúdo ensinou, o que foi implementado e a saída reproduzível está em [`learning-log/2026-11-03-tprm-platform-evidence.md`](learning-log/2026-11-03-tprm-platform-evidence.md).

## Artefatos de risco de terceiros

| Artefato | Comando | Descrição |
|---|---|---|
| `build/tprm-risk-assessment.md` | `python -m tprm --out build risk` | Inerente x residual por fornecedor + concentração por categoria e país. |
| `build/tprm-questionnaire.md` | `python -m tprm --out build questionnaire` | Cobertura do questionário, compliance ponderado e lacunas por fornecedor. |
| `build/tprm-exit-plans.md` | `python -m tprm --out build exit-plan --as-of YYYY-MM-DD` | Checklist DORA Art. 28-30 + runbook de saída para Tier 1. |
| `build/tprm-report.md` | `python -m tprm --out build report --as-of YYYY-MM-DD` | Relatório executivo com o mesmo modelo residual e status contratual por data. |
| `build/tprm-dashboard.html` | `python -m tprm --out build dashboard --as-of YYYY-MM-DD` | Dashboard autocontido com os mesmos números de `risk` e `report`. |

## Como usar para benefício duplo

1. Estude a sala/curso/módulo no link específico.
2. Identifique uma melhoria (pergunta de due diligence, critério de concentração, item de saída).
3. Atualize os CSVs/código.
4. Gere os artefatos: `validate`, `risk`, `questionnaire`, `exit-plan`, `report`.
5. **Commit com menção explícita ao conteúdo real**, por exemplo:
   `feat(tprm): residual risk model from LetsDefend Risk Management (https://app.letsdefend.io/training/lessons/risk-management) - resolves V-004 concentration gap`
6. Registre o write-up em `learning-log/` usando o template.

## Status

- [x] Inerente x residual + concentração por categoria/país (Fase 3)
- [x] Questionário de due diligence + lacunas (Fase 3)
- [x] Planos de saída Tier 1 + runbook (Fase 3)
- [x] Modelo canônico inerente/residual compartilhado por `risk`, `summary`, `report`, `dashboard` e `assessments.csv`
- [x] `validate` compara os ratings salvos nas avaliações com o modelo canônico e detecta divergência
- [x] Status contratual derivado da data; contratos vencidos contam como gap no exit plan
- [x] Referências reais de plataforma (sala/curso/módulo com link direto) no README e neste arquivo
- [x] Write-up de evidência preenchido em `learning-log/2026-11-03-tprm-platform-evidence.md`
- [x] Metadados do GitHub (description/topics) atualizados via API: *Third-party risk management: inherent/residual scoring, due diligence questionnaire, concentration analysis and DORA exit plans*; topics `tprm`, `third-party-risk`, `vendor-risk`, `dora`, `lgpd`, `nist-sp-800-161`, `iso-27001`, `letsdefend`, `hackthebox`, `grc`, `python`, `portfolio`
