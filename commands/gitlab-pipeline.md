---
description: Analisa e corrige pipelines GitLab CI/CD com falhas no MPRJ
---

Analise o estado atual do pipeline GitLab CI/CD deste projeto.

## O que verificar

1. **Status do pipeline atual**
   - Quais jobs estão falhando?
   - Qual é a mensagem de erro exata?
   - É falha de lint, teste, build ou deploy?

2. **Diagnóstico de falhas**
   - Ler o `.gitlab-ci.yml` e identificar problemas de configuração
   - Verificar se as variáveis de ambiente necessárias estão definidas
   - Checar se as imagens Docker estão acessíveis do runner MPRJ
   - Verificar dependências de serviços (PostgreSQL, Redis, etc.)

3. **Correção**
   - Propor correção mínima e específica para o problema
   - Não alterar stages que estão funcionando
   - Manter compatibilidade com runners on-premise do MPRJ

4. **Validação**
   - Após correção, rodar localmente quando possível:
     `gitlab-ci-local` ou equivalente

## Operações via MCP GitLab

Se o MCP GitLab estiver disponível:
- Buscar os logs do último pipeline com falha
- Identificar o job específico que falhou
- Ler a saída do job para diagnóstico preciso

Retorne: diagnóstico → causa raiz → correção proposta → risco da mudança.
