# Conformidade — API Pública do DataJud

Revisão documental: 2026-07-11.

## Premissas incorporadas

- uso apenas dos metadados de processos públicos;
- exclusão de registros com indicação de sigilo;
- nenhuma coleta intencional de dados pessoais de terceiros;
- limite local de 100 requisições por minuto, abaixo do teto de 120 por minuto;
- sem contorno de autenticação ou medida de segurança;
- sem exploração comercial da API ou dos dados derivados;
- sem promessa de precisão, integridade ou atualidade;
- revisão humana obrigatória;
- possibilidade de suspensão, alteração de chave ou indisponibilidade da fonte.

## Operação

A chave pública pode ser lida da variável de ambiente ou, quando habilitado, da
página oficial de acesso do CNJ. Ela permanece somente em memória e nunca é
retornada em health, logs ou payloads.

O gateway de produção deve adicionar limite distribuído e impedir que múltiplas
réplicas ultrapassem o teto agregado.
