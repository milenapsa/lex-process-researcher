# Lex Process Researcher v0.3

Serviço de pesquisa auxiliar de processos públicos para o ecossistema HomoSapiens/Lex.

## O que esta versão resolve

- ativa os aliases oficiais da API Pública do DataJud para os tribunais listados pelo CNJ;
- pesquisa metadados por número CNJ;
- infere automaticamente o TJ estadual quando possível;
- monta linha do tempo a partir dos movimentos retornados;
- obtém a chave pública vigente do DataJud diretamente da página oficial do CNJ, com cache em memória e sem expor a chave;
- preserva fallback para consulta manual oficial quando o portal não permite automação segura;
- registra fonte, momento da coleta, limitações e necessidade de revisão humana;
- não acessa processos sigilosos, não contorna CAPTCHA e não executa protocolo ou peticionamento.

## Execução

```bash
cp .env.example .env
docker compose up --build
```

A API ficará em `http://localhost:8080`.

## Endpoints

- `GET /health`
- `GET /ready`
- `GET /v1/sources`
- `GET /v1/status-matrix`
- `GET /v1/compliance`
- `POST /v1/processes/search`
- `GET /v1/processes/{numero_cnj}?tribunal=tjsc`
- `GET /v1/processes/{numero_cnj}/timeline?tribunal=tjsc`
- `POST /v1/jurisprudence/search`
- `GET /v1/validate-cnj/{numero_cnj}`

## Estados possíveis

- `found`
- `not_found`
- `manual_required`
- `source_unavailable`
- `not_configured`
- `invalid_input`

## Limite jurídico

A resposta é pesquisa auxiliar. A conferência final é humana e a ausência de resultado não prova inexistência do processo.


## Conformidade

O serviço limita a saída para o CNJ a 100 requisições por minuto por instância, exclui registros sigilosos e exige revisão humana. O limite distribuído deve ser aplicado no gateway antes de escalar réplicas.
