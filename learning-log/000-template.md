# Template de write-up - `learning-log/`

Copie este arquivo para `learning-log/YYYY-MM-DD-<plataforma>-<sala>.md` e preencha.
Cada write-up deve apontar para uma mudança rastreável no repositório (commit ou PR).

```md
# <YYYY-MM-DD> - <Plataforma> / <Sala ou trilha>

- **Plataforma:** TryHackMe | LetsDefend | HTB Academy
- **Sala/trilha:** <nome>
- **Link:** <https://...>
- **Artefato do repositório:** <arquivo, comando ou seção do README>
- **Commit:** <hash ou link>

## 1) O que a sala pediu

<Resumo do exercício em 2-4 linhas.>

## 2) O que encontrei no cenário Meridian Pay

<Qual fornecedor (V-xxx), achado ou cláusula contratual se conecta ao exercício.>

## 3) Como o repositório mudou

<O que foi implementado: questionário, risco inerente/residual, concentração,
plano de saída, validação. Explique o "antes" e o "depois" - este é o ponto que
mostra resolução de problema.>

## 4) Evidência

```bash
<comando reproduzível>
```

<Saída resumida ou link para o artefato em build/.>

## 5) Próximo passo

<O que ainda falta e qual sala/trilha pode destravar.>
```

## Regras

1. Uma sala = pelo menos uma melhoria commitada.
2. Sempre cite o link da plataforma e o ID do fornecedor/achado/contrato.
3. A seção **Como o repositório mudou** não pode ser genérica: diga o que quebrava ou faltava.
4. Se a sala não gerou mudança, registre como leitura e não invente evidência.
