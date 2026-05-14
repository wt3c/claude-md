# Quick Start — Claude Code

Guia de início rápido para começar a usar esta configuração do Claude Code em **5 minutos**.

## ⚡ Setup Rápido

### 1. Pré-requisitos

```bash
# Instalar Claude Code
brew install claude-code@latest  # macOS
# ou baixar de https://code.claude.com/docs

# Verificar instalação
claude --version
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env e preencher (mínimo necessário):
# - GITLAB_TOKEN (para MCP GitLab)
# - POSTGRES_CONNECTION_STRING (para MCP PostgreSQL)
```

**Obter tokens:**

- **GitLab Token:** Settings → Access Tokens → Create token (scopes: `api`, `read_repository`)
- **PostgreSQL:** `postgresql://user:password@localhost:5432/database`

### 3. Primeira Sessão

```bash
# Iniciar Claude Code
claude

# Claude automaticamente:
# ✓ Lê CLAUDE.md (instruções do projeto)
# ✓ Carrega .claude/settings.json (hooks, MCP servers)
# ✓ Lê tasks/todo.md (contexto da última tarefa)
# ✓ Executa SessionStart hook (git status + log)
```

## 🎯 Uso Básico

### Comandos Slash

```
/review-pr         → Revisa PR atual
/n1-audit          → Detecta N+1 queries em Django
/check-migrations  → Verifica migrations pendentes
/dynatrace-check   → Consulta métricas no Dynatrace

/status            → Mostra modelo, contexto, sessão
/usage             → Dashboard de uso e custo
/model             → Troca modelo (Sonnet, Opus, Haiku)
/clear             → Limpa histórico
/compact           → Comprime histórico (libera contexto)
```

### Deixar Claude Trabalhar

```
Você: "Preciso criar um service layer para gerenciar pedidos"

Claude:
  [carrega django-service-layer skill automaticamente]
  [aplica padrão Protocol-based DI]
  [cria UserRepository, UserService]
  [escreve testes unitários]
  [auto-formata com ruff via hook]
  ✓ Done!
```

### Skills Automáticas

Claude carrega skills por contexto. Não precisa invocar manualmente.

| Contexto                       | Skill Carregada              |
|--------------------------------|------------------------------|
| "criar service layer Django"   | `django-service-layer`       |
| "otimizar job Spark"           | `pyspark-pipeline`           |
| "desenvolver feature Unity"    | `unity-mobile`               |
| "configurar pipeline GitLab"   | `gitlab-cicd`                |
| "adicionar tracing"            | `opentelemetry-instrumentation` |

## 📋 Workflow Diário

### 1. Início do Dia

```bash
# Retomar última sessão
claude --resume

# Ou nova sessão
claude
```

Claude mostra:
- Git status
- Últimos 5 commits
- Tarefa ativa (tasks/todo.md)

### 2. Desenvolver Feature

```
Você: "Implementar autenticação via Keycloak"

Claude:
1. Cria service layer (UserAuthService)
2. Adiciona testes (TDD)
3. Configura OpenTelemetry tracing
4. Auto-formata código (hook)
5. Executa testes
6. ✓ Feature pronta

Você: /review-pr

Claude: [review completo de segurança, performance, padrões]
```

### 3. Fim do Dia

```
1. Atualizar tasks/todo.md (marcar etapas concluídas)
2. Registrar lições (tasks/lessons.md se houver)
3. Commitar código
```

## 🔍 Exemplos Práticos

### Exemplo 1: Django N+1 Query

```
Você: "Este código tem N+1 queries?"

[colar código Django]

Claude:
  ❌ N+1 detectado na linha 15:
     for user in users:
         print(user.profile.bio)  # query a cada iteração
  
  ✅ Solução:
     users = User.objects.select_related('profile').all()
     for user in users:
         print(user.profile.bio)  # uma query total
```

### Exemplo 2: PySpark Otimização

```
Você: "Otimize este job Spark"

[colar código PySpark]

Claude:
  [carrega pyspark-pipeline skill]
  
  Otimizações sugeridas:
  1. Broadcast join na linha 10 (tabela pequena)
  2. Reparticionar antes do join na linha 15
  3. Cache do DataFrame reutilizado na linha 20
  
  [código otimizado]
```

### Exemplo 3: GitLab CI/CD

```
Você: "Criar pipeline GitLab para este projeto Django"

Claude:
  [carrega gitlab-cicd skill]
  [cria .gitlab-ci.yml otimizado]
  
  Pipeline configurado com:
  - Cache de dependências (UV)
  - Testes paralelos (pytest -n auto)
  - Lint (ruff + mypy)
  - Security scan (bandit)
  - Build Docker
  - Deploy staging (auto) + production (manual)
```

## 🪝 Hooks em Ação

### Auto-Format (Python)

```
Você: [edita arquivo Python]

Claude (hook automático):
  ✓ ruff check app.py --fix
  ✓ ruff format app.py
  → Código formatado automaticamente
```

### Secrets Detection

```
Você: git commit -m "add config"

Claude (hook pré-commit):
  ❌ WARNING: Attempting to commit secrets!
  → .env detectado no staging
  → Commit bloqueado
```

## 🔧 Troubleshooting Rápido

### Problema: Skill não carrega

**Solução:**
```
Mencione explicitamente: "Use a skill django-service-layer"
```

### Problema: Hook não executa

**Solução:**
```bash
# Ver logs detalhados
claude --debug

# Verificar matcher no settings.json
"PostToolUse": [
  {
    "matcher": "Write(*.py)",  # apenas raiz
    vs
    "matcher": "Write(**/*.py)"  # todos os diretórios
  }
]
```

### Problema: MCP server não conecta

**Solução:**
```bash
# Verificar .env
cat .env | grep GITLAB_TOKEN

# Testar servidor manualmente
npx @modelcontextprotocol/server-gitlab

# Ver logs
claude --debug
```

### Problema: Muitos prompts de permissão

**Solução:**
```
/less-permission-prompts

→ Claude analisa histórico e sugere allowlist otimizado
→ Adiciona em .claude/settings.json automaticamente
```

## 📚 Próximos Passos

### Dia 1: Explorar

- [x] Setup inicial (você está aqui!)
- [ ] Testar comandos: `/review-pr`, `/n1-audit`
- [ ] Deixar Claude criar um service layer
- [ ] Verificar auto-format funcionando

### Semana 1: Dominar

- [ ] Criar skill customizada
- [ ] Adicionar comando customizado
- [ ] Configurar hook personalizado
- [ ] Conectar todos MCP servers

### Mês 1: Otimizar

- [ ] Usar prompt caching via API
- [ ] Criar routines (scheduled tasks)
- [ ] Configurar agent teams para revisão paralela
- [ ] Contribuir skills para o time

## 🎓 Recursos

| Recurso                                         | Quando Usar                     |
|-------------------------------------------------|---------------------------------|
| [CLAUDE.md](./CLAUDE.md)                        | Referência completa de padrões  |
| [README.md](./README.md)                        | Visão geral da estrutura        |
| [.claude/README.md](./.claude/README.md)        | Configuração detalhada          |
| [docs/guia-claude-code.md](./docs/guia-claude-code.md) | Guia completo Claude Code |
| [tasks/lessons.md](./tasks/lessons.md)          | Lições aprendidas do projeto    |

## 💡 Dicas Pro

### Produtividade

```
✓ Use /compact em sessões longas (libera contexto)
✓ Use /branch para explorar sem poluir sessão principal
✓ Configure permissões pré-aprovadas (menos prompts)
✓ Deixe skills trabalharem (não microgerencie)
```

### Qualidade

```
✓ Sempre revise diffs antes de aceitar mudanças
✓ Use /review-pr antes de criar PR
✓ Mantenha tasks/lessons.md atualizado
✓ Registre decisões em tasks/decisions.md
```

### Economia

```
✓ Use prompt caching via API (economia ~80%)
✓ Use subagentes para exploração isolada
✓ Configure allowedTools restrito em tarefas simples
✓ Monitore /usage regularmente
```

## 🚀 Começar Agora

```bash
# 1. Setup
cp .env.example .env
# [editar .env com tokens]

# 2. Iniciar
claude

# 3. Primeiro prompt
Você: "Analise este projeto e sugira melhorias de arquitetura"
```

**Pronto! Claude está configurado e pronto para trabalhar.**

---

**Precisa de ajuda?**

- **Documentação:** [CLAUDE.md](./CLAUDE.md) e [README.md](./README.md)
- **Troubleshooting:** Seção acima ou [.claude/README.md](./.claude/README.md)
- **Claude Code Docs:** https://code.claude.com/docs
