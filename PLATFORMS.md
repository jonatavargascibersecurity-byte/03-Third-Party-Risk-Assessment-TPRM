# Plataformas, trilhas e como este repositório se conecta

Este repositório gera **evidência prática** para trilhas de GRC, risco de terceiros e defesa. A regra é: *1 sala/trilha = 1 melhoria commitada, com link e com o problema que foi resolvido*.

## Mapeamento direto

| Plataforma / Trilha / Sala | Foco | Como este repo se relaciona | Como foi aplicado (evidência) |
|---|---|---|---|
| [TryHackMe - Governance & Regulation](https://tryhackme.com/room/cybergovernanceregulation) | Governança, leis/regulamentos, GRC | Due diligence, DPA, transferência internacional e trilha de auditoria. | `questionnaire` cobre 8 perguntas ponderadas (segurança, privacidade, continuidade, subprocessadores, contrato) e calcula compliance por fornecedor. |
| [TryHackMe - Threats & Risks (Risk Management)](https://tryhackme.com/module/threats-and-risks) | Identificar/avaliar/responder/monitorar riscos | Risco inerente x residual por fornecedor e priorização por exposição. | `risk` calcula inerente (criticidade + dados + rede) e residual (compliance + achados), com residual limitado ao inerente; `summary`/`report`/`dashboard` usam o mesmo modelo. |
| [LetsDefend - SOC Manager Path](https://app.letsdefend.io/training) | Triage, avaliação, escalonamento, documentação | Achados de fornecedor com severidade, dono, prazo e evidência. | `findings.csv` + `report`/`dashboard` entregam 16 achados em aberto com dono, prazo, mitigação e evidência. |
| [HTB Academy - SOC Analyst Path](https://academy.hackthebox.com/path/preview/soc-analyst) | Detecção/forense/relatórios | Estrutura de relatório com evidência e recomendação. | `exit-plan` gera checklist verificável por fornecedor Tier 1 e runbook de saída em 7 passos. |
| [HTB - Governance & Compliance](https://www.hackthebox.com/cybersecurity-resources/governance_compliance) | DORA, NIST CSF 2.0, PCI-DSS | DORA Art. 28-30 e LGPD Art. 46/49 aplicados a terceiros. | Concentração por categoria/país (alerta US 26,6%) e planos de saída Tier 1; status contratual é derivado da data (`Vencido`/`Vencendo`/`Ativo`), não de campo manual. |

## Novos artefatos (Fase 3)

| Artefato | Comando | Descrição |
|---|---|---|
| `build/tprm-risk-assessment.md` | `python -m tprm --out build risk` | Inerente x residual por fornecedor + concentração por categoria e país. |
| `build/tprm-questionnaire.md` | `python -m tprm --out build questionnaire` | Cobertura do questionário, compliance ponderado e lacunas por fornecedor. |
| `build/tprm-exit-plans.md` | `python -m tprm --out build exit-plan --as-of YYYY-MM-DD` | Checklist DORA Art. 28-30 + runbook de saída para Tier 1. |

## Como usar para benefício duplo

1. Estude a sala/trilha.
2. Identifique uma melhoria (pergunta de due diligence, critério de concentração, item de saída).
3. Atualize os CSVs/código.
4. Gere os artefatos: `validate`, `risk`, `questionnaire`, `exit-plan`, `report`.
5. **Commit com menção explícita**: `feat(tprm): inherent/residual + country concentration from LetsDefend SOC Manager (https://app.letsdefend.io/training) - resolves V-004 exit gap`.
6. Registre o write-up em `learning-log/` usando o template.

## Status

- [x] Inerente x residual + concentração por categoria/país (Fase 3)
- [x] Questionário de due diligence + lacunas (Fase 3)
- [x] Planos de saída Tier 1 + runbook (Fase 3)
- [x] Modelo canônico inerente/residual compartilhado por `risk`, `summary`, `report`, `dashboard` e `assessments.csv`
- [x] `validate` compara os ratings salvos nas avaliações com o modelo canônico e detecta divergência
- [x] Status contratual derivado da data; contratos vencidos contam como gap no exit plan
- [x] Metadados do GitHub (description/topics) atualizados via API: *Third-party risk management: inherent/residual scoring, due diligence questionnaire, concentration analysis and DORA exit plans*; topics `tprm`, `third-party-risk`, `vendor-risk`, `dora`, `lgpd`, `nist-sp-800-161`, `iso-27001`, `letsdefend`, `hackthebox`, `grc`, `python`, `portfolio`
- [ ] Write-ups preenchidos em `learning-log/` (Fase 5)
