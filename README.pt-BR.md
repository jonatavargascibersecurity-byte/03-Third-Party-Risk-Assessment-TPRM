# Toolkit de Avaliação de Risco de Terceiros (TPRM)

Toolkit de gestão de risco de fornecedores para uma fintech brasileira fictícia (**Meridian Pay**). Cobre tiering de fornecedores, score de risco, acompanhamento de achados e monitoramento de risco contratual.

> **Conteúdos reais que este repositório aplica:** [TryHackMe — Governance & Regulation](https://tryhackme.com/room/cybergovernanceregulation) · [TryHackMe — Risk Management](https://tryhackme.com/room/seriskmanagement) · [LetsDefend — Risk Management](https://app.letsdefend.io/training/lessons/risk-management) · [LetsDefend — Security Product Selection](https://app.letsdefend.io/training/lessons/security-product-selection) · [HTB Academy — Supply Chain Attacks](https://academy.hackthebox.com/course/preview/supply-chain-attacks). Seções, tasks e artefatos estão em [`PLATFORMS.md`](PLATFORMS.md) e no [write-up de evidência](learning-log/2026-11-03-tprm-platform-evidence.md).

## Por que TPRM para entrada

Bancos, fintechs, Big 4 e MSSPs precisam de analistas de risco de terceiros. Este projeto mapeia diretamente para **DORA** (risco de terceiros de TIC), **LGPD** (operador / transferência de dados), **NIST SP 800-161** e **ISO/IEC 27001 A.5.19-A.5.23**.

## Funcionalidades

- **Registro de fornecedores**: criticidade, tier, acesso a dados/rede, responsável, país
- **Risco inerente x residual**: inerente = criticidade + sensibilidade de dados + alcance de rede; residual = inerente - crédito do questionário + achados abertos (limitado ao inerente)
- **Concentração de terceiros**: por categoria e país, com alerta acima de 25% (DORA Art. 29)
- **Avaliações**: registros de due diligence com framework e versão de questionário
- **Achados**: severidade, mitigação, evidência necessária, responsável, prazo
- **Risco contratual**: vencimento, prazo de aviso, plano de saída, addendum de segurança, DPA, subprocessadores
- **Status contratual por data**: `Vencido` / `Vencendo` / `Ativo` é derivado de `end_date`, não de campo manual
- **CLI**: `validate`, `summary`, `vendors`, `findings`, `report`, `dashboard`, `risk`, `questionnaire`, `exit-plan`
- **Sem dependências**: Python puro (stdlib), CSV como fonte única da verdade

## Início rápido

```bash
cd 03-Third-Party-Risk-Assessment-TPRM
pip install -e ".[dev]"
python -m tprm validate
python -m tprm summary --as-of 2026-11-02
python -m tprm vendors
python -m tprm findings
python -m tprm --out build report --as-of 2026-11-02
python -m tprm --out build dashboard --as-of 2026-11-02
python -m tprm --out build risk
python -m tprm --out build questionnaire
python -m tprm --out build exit-plan --as-of 2026-11-02
```

## Alinhamento com plataformas de estudo

Este repositório é um laboratório de prática para trilhas de GRC, risco de terceiros e defesa. Cada conteúdo abaixo é **real e existe na plataforma**; o link aponta para a sala/curso/módulo específico, não para a home da plataforma.

| Plataforma / conteúdo real | Link | O que o conteúdo cobre | Onde o repositório aplica |
|---|---|---|---|
| **TryHackMe — Governance & Regulation** (sala) | https://tryhackme.com/room/cybergovernanceregulation | Framework GRC, ISO/IEC 27001, SOC 2, NIST SP 800-53, privacidade e proteção de dados | `data/questionnaire.csv` (Q05 DPA/LGPD, Q07 subprocessadores, Q08 auditoria) e `data/contracts.csv` (`dpa_signed`, `security_addendum`, `subprocessors_required`) |
| **TryHackMe — Risk Management** (sala) | https://tryhackme.com/room/seriskmanagement | Ciclo Frame → Assess → Respond → Monitor; risco de supply chain no monitoramento | `src/tprm/vendorrisk.py` (`inherent_points`, `residual_points`, `concentration`, `contract_timing`) e os artefatos `risk`, `report`, `dashboard` |
| **LetsDefend — Risk Management** (curso) | https://app.letsdefend.io/training/lessons/risk-management | Terminologia, framework, avaliação passo a passo e cálculo quantitativo vs qualitativo | `src/tprm/scales.py` (escala 0-10, níveis Crítico/Alto/Moderado/Baixo) e a regra `residual <= inerente` |
| **LetsDefend — Security Product Selection** (SOC Manager) | https://app.letsdefend.io/training/lessons/security-product-selection | Requisitos técnicos/negócio e comparação estruturada de fornecedores | `data/vendors.csv` (`tier`, `criticality`) + `data/questionnaire.csv` (pesos 1-3) e cobertura de due diligence |
| **HTB Academy — Supply Chain Attacks** (módulo) | https://academy.hackthebox.com/course/preview/supply-chain-attacks | Ciclo do ataque, supply chain de hardware/software, vetores, SolarWinds, insider threats e mitigação | `subprocessors_required` no contrato, `exit-plan` Tier 1 e concentração por categoria/país (DORA Art. 28-29) |

Os cinco conteúdos foram verificados em 2026-11-03. O detalhamento de cada seção/task, o que foi aprendido e a evidência reproduzível estão em [`learning-log/2026-11-03-tprm-platform-evidence.md`](learning-log/2026-11-03-tprm-platform-evidence.md) e no mapeamento completo em [`PLATFORMS.md`](PLATFORMS.md).

### Artefatos de risco de terceiros

| Comando | Saída | Para que serve |
|---|---|---|
| `python -m tprm --out build risk` | `build/tprm-risk-assessment.md` | Inerente x residual por fornecedor + concentração por categoria e país (DORA Art. 29). |
| `python -m tprm --out build questionnaire` | `build/tprm-questionnaire.md` | Cobertura, compliance ponderado e lacunas por fornecedor. |
| `python -m tprm --out build exit-plan --as-of YYYY-MM-DD` | `build/tprm-exit-plans.md` | Checklist Tier 1 (DORA Art. 28-30) + runbook de saída em 7 passos. |
| `python -m tprm --out build report --as-of YYYY-MM-DD` | `build/tprm-report.md` | Relatório executivo com o mesmo modelo residual e status contratual por data. |
| `python -m tprm --out build dashboard --as-of YYYY-MM-DD` | `build/tprm-dashboard.html` | Dashboard autocontido com os mesmos números de `risk` e `report`. |

O risco residual nunca ultrapassa o inerente: achados erodem o benefício dos controles, não criam exposição nova. Contratos vencidos contam como gap no exit plan, mesmo que o campo `status` do CSV esteja desatualizado. O template de write-up está em [`learning-log/000-template.md`](learning-log/000-template.md).

## Estrutura de dados

- `data/vendors.csv` - registro de fornecedores
- `data/assessments.csv` - avaliações de due diligence; `inherent_risk`/`overall_risk` (pré-mitigação) e `residual_risk` (pós-mitigação) são validados contra o modelo canônico por `python -m tprm validate`
- `data/findings.csv` - achados e mitigações
- `data/contracts.csv` - monitoramento de contratos e cláusulas
- `data/questionnaire.csv` - perguntas de due diligence (peso, evidência esperada)
- `data/questionnaire_responses.csv` - respostas por fornecedor com evidência

## Licença

MIT
