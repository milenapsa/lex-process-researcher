# Handoff de execução — Lex ↔ Platform Core

**Uso:** continuidade entre janelas  
**Classificação:** A3  
**Execução real:** depende do runner/CI da janela operadora

## Papel desta janela Lex

A janela que possui o runner operacional deve:

1. preservar o desenvolvimento atual da Lex;
2. ler o estado mais recente da `main` antes de qualquer alteração;
3. validar o contrato de integração com o Platform Core;
4. executar testes e registrar evidência;
5. não promover HML ou produção sem aprovação A4.

## Contrato atual usado pelo Platform Core

O consumidor está preparado para:

- `GET /health`;
- `POST /v1/processes/search`.

O consumidor não deve usar, por enquanto:

- `GET /v1/processes/{numero_cnj}`;
- `GET /v1/processes/{numero_cnj}/timeline`.

Motivo: o CNJ no caminho pode aparecer em logs, proxies e traces.

## Requisitos de resposta

Para resultados substantivos (`found`, `not_found`, `manual_required`):

- `evidence` obrigatória;
- `evidence.official: true`;
- `human_review_required: true`;
- `records` coerentes com o status;
- `limitations` como lista de textos;
- nenhum segredo retornado.

Para estados operacionais (`not_configured`, `source_unavailable`, `rate_limited`, `invalid_input
J,

- podem existir sem fonte oficial;
- não podem transportar registros;
- revisão humana permanece obrigatória;
- devem declarar limitações.

## Teste integrado seguro

Executar somente com fixture sintética:

1. iniciar servidor Lex local ou fake server;
2. chamar `POST /v1/processes/search`;
3. confirmar que o Core reduz registros a referências opacas;
4. confirmar que CNJ não aparece no evento persistido;
5. confirmar que resultado sem fonte oficial é rejeitado;
6. confirmar que estado operacional sem registros é aceito;
7. confirmar circuit breaker, timeout e limite de resposta.

## Evidência

Registrar:

- commit da Lex;
- commit do Platform Core;
- quantidade de testes;
- zero falhas;
- saída do runner;
- nenhum credencial;
- nenhum dado real;
- deploy, VPS e DNS como não executados.

## Pendência de produto

Criar rota segura:

`POST /v1/processes/timeline`

O CNJ deve ficar no corpo JSON, nunca na URL, query string ou logs.

## Regra final

Sem saída técnica do runner ou do CI, registrar apenas `preparado` ou `enfileirado`, nunca `executado com sucesso`.
