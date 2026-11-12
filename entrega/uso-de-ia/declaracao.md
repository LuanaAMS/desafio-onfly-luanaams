# Declaração de uso de IA

## Ferramenta e modelo
- **Ferramenta:** Claude Code (app desktop da Anthropic), com navegador embutido e terminal.
- **Modelo:** Claude Sonnet 5.5 (`claude-sonnet-5-5`).
- **Revisão de código:** skill `bmad-code-review` do BMad Method v6.12.4 (instalado só para a revisão),
  executada com 4 subagentes revisores (Blind Hunter, Edge Case Hunter, Verification Gap e
  Acceptance Auditor), cada um rodando no mesmo modelo.
- **Ambiente:** Python 3.12 e `uv` baixados para uma pasta local do projeto, sem instalação global.

## O que a IA fez
- Leu o README do desafio e o código do projeto.
- Rodou `pytest` (5 falhas iniciais), identificou os 5 defeitos e aplicou as correções
  (câmbio, noites, política de status, ordenação do ranking e truncamento em 200 linhas).
- Validou o resultado com a amostra do README e recalculou o relatório completo por um script
  independente.
- Rodou a revisão de código do BMad, triou os achados contra os dados reais e aplicou os patches
  aprovados: moeda sem taxa como erro de entrada, arquivo não UTF-8 como erro de entrada, aceitação
  de BOM e 7 testes novos em `tests/test_review_regressions.py`.
- Escreveu `entrega/README-ENTREGA.md` e esta declaração, e ajustou o `.gitignore`.

## O que a pessoa fez
- Trouxe o desafio e pediu a análise inicial e a correção.
- Propós o uso do BMad-Code-Review.
- Revisou todos os retornos da IA.
- Autorizou os downloads e as instalações (projeto, `uv`, Python, BMad).
- Aprovou a aplicação dos patches da revisão.
- Responsável por conferir o resultado, publicar o repositório e enviar o formulário.


## Sobre a exportação da sessão
`sessao-01.jsonl` é a exportação nativa do Claude Code (transcrição da sessão principal). Os
transcritos dos 4 subagentes revisores não foram incluídos: o que eles reportaram está resumido na
seção de revisão de código do `README-ENTREGA.md`. Antes de publicar, foram removidos da exportação
dados pessoais e de outros projetos (e-mail, nome de usuário do Windows, nomes de pessoas e de uma
organização que vinham de instruções privadas), substituídos por marcadores `[...-redigido]`. O
conteúdo técnico da conversa não foi alterado.
