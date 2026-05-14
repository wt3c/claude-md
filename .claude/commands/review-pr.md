---
description: Revisa o PR atual para qualidade, segurança e conformidade com padrões do projeto
---

Revise o diff atual considerando:

## 1. Segurança
- [ ] Sem secrets, tokens ou credenciais hardcoded
- [ ] Sem SQL injection, XSS, command injection
- [ ] Validação de input em endpoints públicos
- [ ] Autenticação e autorização implementadas corretamente
- [ ] Dados sensíveis não logados ou expostos

## 2. Performance
- [ ] N+1 queries (Django: select_related, prefetch_related)
- [ ] Índices de banco adequados para queries novas
- [ ] Queries desnecessárias ou ineficientes
- [ ] Cache apropriado para dados frequentemente acessados
- [ ] PySpark: collect(), broadcast joins, particionamento

## 3. Padrões do Projeto (CLAUDE.md)
- [ ] Service Layer pattern aplicado (Django)
- [ ] Protocol-based DI em vez de herança
- [ ] TDD: testes escritos antes do código
- [ ] Comentários em português, identificadores em inglês
- [ ] Commits atômicos e rastreáveis

## 4. Qualidade de Código
- [ ] Cobertura de testes ≥ 80% em código novo
- [ ] Lint passando (ruff check, mypy)
- [ ] Sem code smells (duplicação, complexidade excessiva)
- [ ] Documentação adequada (docstrings, README se aplicável)
- [ ] Sem TODOs sem data/responsável

## 5. Testes
- [ ] Testes unitários para lógica de negócio
- [ ] Testes de integração para APIs
- [ ] Edge cases cobertos
- [ ] Testes de caracterização antes de refatoração (legado)

## Formato de Saída

```markdown
# Review do PR

## ✅ Aprovado / ⚠️ Atenção / ❌ Crítico

### Segurança
- [status] [descrição do achado]

### Performance
- [status] [descrição do achado]

### Padrões
- [status] [descrição do achado]

### Qualidade
- [status] [descrição do achado]

### Testes
- [status] [descrição do achado]

## Resumo
[Resumo geral: aprovar, solicitar mudanças, ou bloquear]

## Recomendações
1. [ação recomendada 1]
2. [ação recomendada 2]
```
