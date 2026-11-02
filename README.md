# Toolkit de Avaliação de Risco de Terceiros (TPRM)

Toolkit de gestão de risco de fornecedores para uma fintech brasileira fictícia (**Meridian Pay**). Cobre tiering de fornecedores, score de risco, acompanhamento de achados e monitoramento de risco contratual.

## Por que TPRM para entrada

Bancos, fintechs, Big 4 e MSSPs precisam de analistas de risco de terceiros. Este projeto mapeia diretamente para **DORA** (risco de terceiros de TIC), **LGPD** (operador / transferência de dados), **NIST SP 800-161** e **ISO/IEC 27001 A.5.19-A.5.23**.

## Funcionalidades

- **Registro de fornecedores**: criticidade, tier, acesso a dados/rede, responsável, país
- **Score de risco**: criticidade + achados Críticos/Altos em aberto (ponderado)
- **Avaliações**: registros de due diligence com framework e versão de questionário
- **Achados**: severidade, mitigação, evidência necessária, responsável, prazo
- **Risco contratual**: vencimento, prazo de aviso, plano de saída, addendum de segurança, DPA, subprocessadores
- **CLI**: `validate`, `summary`, `vendors`, `findings`, `report`, `dashboard`
- **Sem dependências**: Python puro (stdlib), CSV como fonte única da verdade

## Início rápido

```bash
cd 03-Third-Party-Risk-Assessment-TPRM
pip install -e ".[dev]"
python -m tprm validate
python -m tprm summary
python -m tprm vendors
python -m tprm findings
python -m tprm --out build report
python -m tprm --out build dashboard
python -m tprm --out build risk
python -m tprm --out build questionnaire
python -m tprm --out build exit-plan --as-of 2026-11-02
```

## Alinhamento com plataformas de estudo

Este repositório é um laboratório de prática para trilhas de GRC, risco de terceiros e defesa. Cada sala/trilha vira uma melhoria rastreável; o mapeamento completo (plataforma, link, artefato e o que foi resolvido) está em [`PLATFORMS.md`](PLATFORMS.md).

| Plataforma / trilha | Link | Como o repositório aplica |
|---|---|---|
| TryHackMe - Governance & Regulation | [sala](https://tryhackme.com/room/cybergovernanceregulation) | Due diligence, DPA, transferência internacional e trilha de auditoria em 8 perguntas. |
| TryHackMe - Threats & Risks | [módulo](https://tryhackme.com/module/threats-and-risks) | Risco inerente x residual por fornecedor e priorização por exposição. |
| LetsDefend - SOC Manager Path | [trilha](https://app.letsdefend.io/training) | Achados com severidade, dono, prazo e evidência no formato de avaliação. |
| HTB Academy - SOC Analyst Path | [trilha](https://academy.hackthebox.com/path/preview/soc-analyst) | Relatório e checklist de saída com itens verificáveis. |
| HTB - Governance & Compliance | [recursos](https://www.hackthebox.com/cybersecurity-resources/governance_compliance) | DORA Art. 28-30 e LGPD Art. 46/49 aplicados a terceiros. |

### Artefatos de risco de terceiros

| Comando | Saída | Para que serve |
|---|---|---|
| `python -m tprm --out build risk` | `build/tprm-risk-assessment.md` | Inerente x residual por fornecedor + concentração por categoria e país (DORA Art. 29). |
| `python -m tprm --out build questionnaire` | `build/tprm-questionnaire.md` | Cobertura, compliance ponderado e lacunas por fornecedor. |
| `python -m tprm --out build exit-plan --as-of YYYY-MM-DD` | `build/tprm-exit-plans.md` | Checklist Tier 1 (DORA Art. 28-30) + runbook de saída em 7 passos. |

O risco residual nunca ultrapassa o inerente: achados erodem o benefício dos controles, não criam exposição nova. O template de write-up está em [`learning-log/000-template.md`](learning-log/000-template.md).

## Estrutura de dados

- `data/vendors.csv` - registro de fornecedores
- `data/assessments.csv` - avaliações de due diligence
- `data/findings.csv` - achados e mitigações
- `data/contracts.csv` - monitoramento de contratos e cláusulas
- `data/questionnaire.csv` - perguntas de due diligence (peso, evidência esperada)
- `data/questionnaire_responses.csv` - respostas por fornecedor com evidência

## Licença

MIT
