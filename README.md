# Third-Party Risk Assessment (TPRM) Toolkit

Vendor risk management toolkit for a fictional Brazilian fintech (**Meridian Pay**). Covers vendor tiering, risk scoring, findings tracking and contract risk monitoring.

## Why TPRM entry-level

Banks, fintechs, Big 4 and MSSPs need third-party risk analysts. This project maps directly to **DORA** (ICT third-party risk), **LGPD** (data processor / transfer), **NIST SP 800-161** and **ISO/IEC 27001 A.5.19-A.5.23**.

## Features

- **Vendor register**: criticality, tier, data/network access, ownership, country
- **Risk scoring**: criticality + open Critical/High findings (weighted)
- **Assessments**: due diligence records with framework and questionnaire version
- **Findings**: severity, mitigation, evidence required, owner, target date
- **Contract risk**: expiry, notice period, exit plan, security addendum, DPA, subprocessors
- **CLI**: `validate`, `summary`, `vendors`, `findings`, `report`, `dashboard`
- **Zero deps**: pure Python stdlib, CSV single source of truth

## Quick start

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

## Data model

- `data/vendors.csv` - vendor register
- `data/assessments.csv` - due diligence assessments
- `data/findings.csv` - findings and mitigations
- `data/contracts.csv` - contract and clause monitoring

## License

MIT
