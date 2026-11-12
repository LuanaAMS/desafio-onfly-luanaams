# Entrega — Consolidador de reservas de hotel

Resultado: `pytest -q` → **12 passed** (5 fornecidos, sem alteração, + 7 novos). A amostra
`data/exemplo-validacao.csv` reproduz exatamente os valores do README (12 reservas, 9 confirmadas,
28 noites, R$ 7566.00, média 270.21, `by_month` e `top_hotels` idênticos). O dataset completo
(`data/reservas_hoteis.csv`) agora processa as 300 linhas (antes eram 200).

## Defeitos corrigidos

| # | Arquivo | Defeito | Causa raiz |
|---|---------|---------|-----------|
| 1 | `services/currency_converter.py` | Valores em BRL errados | Dividia por `rate_to_brl` em vez de multiplicar, e passava por `float`. |
| 2 | `services/stay_calculator.py` | Noites erradas (até negativas) na virada de mês/ano | Usava `checkout.day - checkin.day` em vez da diferença de datas. |
| 3 | `services/status_policy.py` | `NO_SHOW` entrava nos totais | `is_billable` era `status != "CANCELLED"`; só `CONFIRMED` é faturável. |
| 4 | `services/report_builder.py` | `top_hotels` com os hotéis de menor valor | Ordenava ascendente por valor; o correto é decrescente, com desempate por `hotel_id` ascendente. |
| 5 | `repositories/csv_reservation_repository.py` | Reservas descartadas silenciosamente | Havia um `break` ao chegar em 200 linhas, truncando o arquivo. |

## Endurecimento adicional (revisão de código)
Uma revisão adversarial (BMad `code-review`) não encontrou novos defeitos nos dados fornecidos; o
resultado foi conferido recalculando o relatório completo por fora (1347 noites, R$ 396170.00).
Aplicados apenas ajustes de baixo risco:
- Moeda sem taxa agora é erro de entrada (`InputFileError`, saída 2) em vez de `KeyError` (saída 1).
- Arquivo que não é UTF-8 vira `InputFileError` (saída 2); CSV com BOM (Excel) é aceito (`utf-8-sig`).
- Novos testes em `tests/test_review_regressions.py` (os fornecidos não foram alterados):
  `by_month`, arredondamento half-up só na serialização, desempate por `hotel_id` e `--top`,
  entrada sem confirmadas, BOM, moeda sem taxa e arquivo não UTF-8. Total: 12 testes passando.

## Como investiguei
Rodei `pytest -q` (5 falhas), li o README para extrair as regras de negócio e comparei cada serviço
com a regra correspondente. Cada falha de teste apontou para um dos defeitos 1–4. O defeito 5 não
tinha teste: apareceu ao conferir que o CSV completo tem 300 reservas e o relatório contava só 200.

## Como validei
- `pytest -q` com os testes fornecidos inalterados.
- CLI na amostra de validação, comparando campo a campo com a tabela do README.
- CLI no CSV completo: 300 reservas lidas.

```bash
pip install -r requirements-dev.txt
pytest -q
PYTHONPATH=src python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
```

## O que não mudou
Comando e argumentos do CLI, schema/semântica do relatório, `data/reservas_hoteis.csv`,
`data/taxas_cambio.csv` e os testes fornecidos.
