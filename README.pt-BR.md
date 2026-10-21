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
python -m tprm report --out build
python -m tprm dashboard --out build
```

## Estrutura de dados

- `data/vendors.csv` - registro de fornecedores
- `data/assessments.csv` - avaliações de due diligence
- `data/findings.csv` - achados e mitigações
- `data/contracts.csv` - monitoramento de contratos e cláusulas

## Licença

MIT
