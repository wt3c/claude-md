---
description: Revisa o MR/PR atual para qualidade, segurança e padrões do projeto
---

Revise o diff atual (git diff main...HEAD ou diff do MR aberto) considerando:

1. **Segurança**
   - Injection (SQL, command, path traversal)
   - Secrets ou credenciais expostas
   - Autenticação e autorização inadequadas
   - Dados sensíveis em logs ou respostas

2. **Performance**
   - N+1 queries (verificar select_related/prefetch_related)
   - Índices ausentes em colunas filtradas/ordenadas
   - Queries sem paginação
   - Operações custosas em loops

3. **Padrões do projeto (CLAUDE.md)**
   - TDD respeitado (todo código tem teste)
   - Cobertura ≥ 80% em código novo
   - Ruff + mypy sem erros
   - Sem lógica de negócio em views
   - Secrets via Infisical
   - UV para dependências

4. **Qualidade geral**
   - Commits atômicos e mensagens claras
   - Sem código comentado ou dead code
   - Docstrings em inglês onde necessário
   - Comentários explicativos em português (somente onde o WHY não é óbvio)

Retorne um relatório estruturado com:
- **CRÍTICO** — deve ser corrigido antes do merge
- **ATENÇÃO** — deve ser discutido
- **SUGESTÃO** — melhoria opcional
- **OK** — aprovado sem ressalvas
