# Canônico — Lex Process Researcher v0.3.0

**Estado:** canônico operacional e técnico.  
**Data:** 2026-07-11.  
**Destino:** HomoSapiens / Lex.  
**Repositório:** `milenapsa/lex-process-researcher`.  
**Natureza:** pesquisa auxiliar de processos públicos e fontes jurisprudenciais oficiais.  
**Não é:** peticionamento, protocolo, decisão jurídica, acesso a autos sigilosos ou automação de credenciais.

## 1. Objetivo

Construir uma camada única de pesquisa para a Lex capaz de:

1. receber número CNJ, tribunal, tese ou termo;
2. selecionar a fonte oficial adequada;
3. consultar metadados públicos;
4. normalizar resultados;
5. registrar fonte, horário, limitações e estado da consulta;
6. montar linha do tempo quando houver movimentos;
7. encaminhar para consulta manual oficial quando a automação não for permitida;
8. entregar pesquisa auxiliar sujeita a revisão humana.

## 2. Regra de evidência

Nenhum resultado será tratado como atual, completo ou existente sem retorno da fonte oficial.

Ausência de resultado significa apenas que a fonte consultada não retornou registro naquele momento.  
Não significa inexistência do processo, baixa, trânsito em julgado ou ausência de movimentação.

Toda resposta deve conter:

- consulta executada;
- tribunal ou fonte selecionada;
- URL ou identificador da fonte;
- data e hora da coleta;
- estado técnico;
- registros encontrados;
- limitações;
- indicação de revisão humana.

## 3. Fontes

### DataJud

A camada DataJud é a fonte automática prioritária para capas processuais e movimentações públicas.

Inventário oficial atual: **91 aliases**, distribuídos em:

- 4 tribunais superiores;
- 6 Tribunais Regionais Federais;
- 27 Tribunais de Justiça estaduais;
- 24 Tribunais Regionais do Trabalho;
- 27 Tribunais Regionais Eleitorais;
- 3 Tribunais de Justiça Militar estaduais.

O arquivo `config/sources.datajud.json` é a fonte de configuração versionada.

### TJSC/eproc

O portal completo do TJSC/eproc permanece híbrido:

- DataJud para metadados públicos;
- portal oficial para conferência manual;
- nenhuma tentativa de contornar CAPTCHA, autenticação, chave de processo, 2FA ou limitação técnica.

### Jurisprudência

A expansão por tribunal deverá classificar cada fonte como:

- `official_api`;
- `official_dataset`;
- `official_curated_page`;
- `manual_official`;
- `unavailable`;
- `blocked_by_policy`.

Jurisprudência integral somente será automatizada por API, dataset ou permissão oficial compatível.

## 4. Chave pública do DataJud

Estratégia obrigatória:

1. usar `DATAJUD_API_KEY` do ambiente quando configurada;
2. caso ausente, consultar a página oficial de acesso;
3. extrair somente a chave pública vigente;
4. manter cache curto apenas em memória;
5. nunca gravar a chave no Git, banco, arquivo, log ou resposta da API;
6. invalidar o cache em `401` ou `403`;
7. nunca retornar a chave em health ou diagnóstico.

## 5. Estados técnicos

- `found`: registro retornado;
- `not_found`: fonte respondeu sem registro;
- `manual_required`: conferência humana necessária;
- `source_unavailable`: fonte indisponível;
- `not_configured`: conector ainda não operacional;
- `invalid_input`: entrada inválida;
- `rate_limited`: limite da fonte atingido.

## 6. Privacidade

Número CNJ, nomes de partes e conteúdo processual são dados potencialmente pessoais.

Regras:

- não registrar payload processual completo em log;
- não registrar nomes de partes por padrão;
- não registrar cabeçalhos de autenticação;
- usar `correlation_id` sem dado pessoal;
- cache somente quando necessário e com retenção definida;
- excluir processos sigilosos;
- minimizar campos retornados à finalidade da pesquisa.

## 7. Autonomia A0–A4

- **A0:** análise, documentação e planejamento.
- **A1:** health, leitura de fontes e inventário.
- **A2:** dry-run, testes locais e preview.
- **A3:** gravação reversível no repositório e integração em branch controlada.
- **A4:** deploy, publicação, alteração de VPS, Docker, DNS ou produção.

Este canônico autoriza o trabalho documental e de repositório já aprovado.  
Deploy A4 exige snapshot ou backup, serviço-alvo identificado, teste canário, pós-teste e rollback.

## 8. Critérios de pronto

Uma fonte só pode ser marcada `automatic_active` quando houver:

- contrato documentado;
- health;
- teste positivo;
- teste de ausência;
- tratamento de timeout;
- tratamento de limite;
- fonte e data na resposta;
- logs seguros;
- revisão de termos de uso;
- rollback ou desativação simples.

## 9. Integração HomoSapiens/Lex

A integração deverá preservar as rotas existentes da Lex.

Fluxo:

`cliente -> gateway Lex -> roteador de pesquisa -> conector oficial -> normalizador -> evidência -> resposta`

O runtime principal deve poder desativar cada connector por feature flag.

## 10. Proifições

É proibido:

- CAPTCHA bypass;
- scraping contra vedação expressa;
- uso de credenciais de usuário;
- certificado digital, PFX ou 2FA;
- acesso a autos sigilosos;
- protocolo ou peticionamento;
- conclusão jurídica automática;
- promessa de completude ou atualidade;
- exposição da chave pública em código, log ou resposta.

## 11. Regra final

Preparar não é publicar.  
Commit não é deploy.  
Issue não é integração.  
Fonte mapeada não é fonte ativa.  
Sem evidência técnica, não afirmar execução em produção.
