# 2026-11-03 — Evidência de plataformas no TPRM

Este write-up registra **conteúdo real** estudado nas plataformas e a mudança correspondente neste repositório. Os links abaixo abrem a sala, o curso ou o módulo específico — não a home da plataforma.

| Plataforma | Conteúdo real | Link | Seções/tasks usadas | Artefato do repositório |
|---|---|---|---|---|
| TryHackMe | Governance & Regulation (sala) | https://tryhackme.com/room/cybergovernanceregulation | Task 4 (GRC), Task 5 (Privacy and Data Protection), Task 6 (NIST Special Publications), Task 7 (ISO/IEC 27001 e SOC 2) | `data/questionnaire.csv`, `data/contracts.csv` |
| TryHackMe | Risk Management (sala) | https://tryhackme.com/room/seriskmanagement | Basic Terminology; Risk Assessment; Risk Management Process (Frame → Assess → Respond → Monitor); supply chain risk no monitoramento | `src/tprm/vendorrisk.py`, `build/tprm-risk-assessment.md` |
| LetsDefend | Risk Management (curso) | https://app.letsdefend.io/training/lessons/risk-management | Introduction; Terminology; Framework; Risk Assessment Step By Step; Risk Calculation Issue; Quantitative vs Qualitative | `src/tprm/scales.py`, `src/tprm/vendorrisk.py` |
| LetsDefend | Security Product Selection (SOC Manager) | https://app.letsdefend.io/training/lessons/security-product-selection | Organizational Needs and Budget Constraints; Comparative Analysis of Security Products; Decision-Making Strategies in Product Selection | `data/vendors.csv`, `data/questionnaire.csv` |
| HTB Academy | Supply Chain Attacks (módulo) | https://academy.hackthebox.com/course/preview/supply-chain-attacks | Introduction to Supply Chains; Lifecycle of a Supply Chain Attack; Software Supply Chain Attacks; Common Attack Vectors; The SolarWinds Attack; Insider Threats | `data/contracts.csv`, `build/tprm-exit-plans.md` |

**Commit deste write-up:** `git log -1 --format=%H -- learning-log/2026-11-03-tprm-platform-evidence.md`

## 1) O que cada conteúdo pediu

### TryHackMe — Governance & Regulation

A sala percorre o framework GRC e os componentes de governança, gestão de risco e conformidade. Na parte de privacidade e proteção de dados, discute leis e regulamentos (GDPR, PCI DSS, LGPD no contexto do projeto) e, em *Information Security Management and Compliance*, apresenta ISO/IEC 27001 e SOC 2. O ponto cobrado é: due diligence de terceiros precisa de base legal, finalidade, DPA e cláusulas verificáveis — não basta um “sim” no fornecedor.

### TryHackMe — Risk Management

A sala apresenta terminologia de risco, avaliação e o processo **Frame → Assess → Respond → Monitor**. No monitoramento, inclui risco de supply chain: acompanhar terceiros e dependências depois da contratação, não apenas no onboarding.

### LetsDefend — Risk Management

O curso cobre terminologia, framework, avaliação passo a passo, problemas de cálculo e a diferença entre cálculo quantitativo e qualitativo. O aprendizado aplicado foi separar **risco inerente** (exposição antes de controles) de **residual** (depois de questionário e achados), sem deixar o residual ultrapassar o inerente.

### LetsDefend — Security Product Selection

A lição do SOC Manager trata de requisitos organizacionais e orçamento, análise comparativa de produtos de segurança e estratégias de decisão. O aprendizado aplicado foi comparar fornecedores por critérios estruturados e pesos, em vez de um score único baseado só em criticidade.

### HTB Academy — Supply Chain Attacks

O módulo cobre o ciclo de um ataque de supply chain, cadeias de hardware e software, vetores comuns, insider threats e casos como SolarWinds e Target. O aprendizado aplicado foi tratar **subprocessadores e quartos** como parte da exposição do fornecedor e exigir plano de saída/lista de subprocessadores.

## 2) O que encontrei no cenário Meridian Pay

- **V-004 DataScan** é Tier 1, tem acesso a dados sensíveis e concentra achados Críticos; o residual fica **Crítico (8)**.
- **V-009 CodeRepoPro** é Tier 1, acesso a repositório de código, e também fica **Crítico (8)** no residual.
- **16 achados abertos**, sendo 3 Críticos; 2 fornecedores com residual Crítico e 7 com residual Alto.
- **10 fornecedores**, mas apenas **5 avaliados** pelo questionário (cobertura de 50%).
- **4 contratos vencidos** em 2026-11-02 (CT-003, CT-005, CT-006, CT-008) e **2 vencendo em 90 dias** (CT-001 e CT-009). O CT-008 venceu em 2026-11-01, um dia antes da data de referência.
- Concentração por país: **EUA 26,6%**, acima do limite de 25% usado no alerta DORA Art. 29.

## 3) Como o repositório mudou

| Antes | Depois | Onde |
|---|---|---|
| Score único `criticality + achados` (`vendor_risk`) | Modelo canônico **inerente + residual** com teto `residual <= inerente` | `src/tprm/scales.py`, `src/tprm/vendorrisk.py` |
| `report`, `dashboard` e `summary` podiam divergir do `risk` | Todos usam `assess_vendors`; `assessments.csv` é validado contra o modelo | `src/tprm/report.py`, `src/tprm/dashboard.py`, `src/tprm/cli.py`, `src/tprm/loader.py` |
| Status contratual era campo manual e CT-008 estava `Ativo` com `end_date` vencido | Status derivado de `end_date` (`Vencido`/`Vencendo`/`Ativo`) e contrato vencido vira gap no exit plan | `src/tprm/vendorrisk.py` (`contract_timing`), `data/contracts.csv` |
| Questionário existia, mas sem cobrança de consistência | `validate` checa duplicados, severidade/status, datas, pesos, respostas e divergência vendor/contrato | `src/tprm/loader.py`, `src/tprm/vendorrisk.py` (`assessment_consistency_issues`) |
| Links de plataforma genéricos | Links diretos para sala/curso/módulo, com seções/tasks e artefato correspondente | `README.md`, `PLATFORMS.md`, este write-up |

## 4) Evidência reproduzível

```bash
cd 03-Third-Party-Risk-Assessment-TPRM
export PYTHONPATH=src   # PowerShell: $env:PYTHONPATH="src"

python -m tprm validate
python -m tprm summary --as-of 2026-11-02
python -m tprm --out build risk
python -m tprm --out build questionnaire
python -m tprm --out build exit-plan --as-of 2026-11-02
python -m pytest -q
```

Saída resumida em 2026-11-03:

```text
OK - TPRM data quality checks passed.
Vendors                    : 10
Assessments                : 10
Open findings              : 16
Vendors residual C/H       : 2/7
Contracts expired/expiring : 4/2

vendors assessed: 5/10
V-004 DataScan      70.0%
V-009 CodeRepoPro   82.5%
V-010 LogHub       100.0%
V-001 SecureAuth    87.5%
V-002 TransactBridge 87.5%

EXIT PLANS (Tier 1)
  V-001 SecureAuth Ltd   OK  gaps=0 pending=2
  V-009 CodeRepoPro      OK  gaps=0 pending=2
  V-004 DataScan         OK  gaps=0 pending=2
  V-002 TransactBridge   OK  gaps=0 pending=2
  V-010 LogHub           OK  gaps=0 pending=2

11 passed
```

## 5) Próximo passo

- Fechar os 16 achados abertos, priorizando V-004 e V-009 (residual Crítico).
- Renovar ou formalizar saída dos contratos vencidos CT-003, CT-005, CT-006 e CT-008.
- Completar o questionário dos 5 fornecedores ainda não avaliados (V-003, V-005, V-006, V-007, V-008).
- Revisar a concentração EUA (26,6%) e registrar um plano de diversificação.
