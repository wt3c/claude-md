# Claude Code — Configuração Global Multi-Stack

Configuração completa e robusta do Claude Code para desenvolvimento multi-stack (Python/Django, PySpark/Airflow, Unity/Android).

## 🎯 Overview

Este repositório contém:

- **CLAUDE.md** — Constituição do projeto (instruções, padrões, checklists)
- **Skills** — Expertise automatizada por contexto
- **Commands** — Comandos customizados (slash commands)
- **Hooks** — Automação de ciclo de vida
- **MCP Servers** — Integrações externas (GitLab, PostgreSQL, Dynatrace, etc.)
- **Tasks** — Sistema de gestão de tarefas e lições aprendidas

## 📁 Estrutura

```
.
├── CLAUDE.md                    # Constituição do projeto (IMPORTANTE!)
├── README.md                    # Este arquivo
├── .env.example                 # Template de variáveis de ambiente
├── .gitignore                   # Git ignore (inclui .env, secrets, etc.)
│
├── .claude/                     # Configuração Claude Code
│   ├── README.md                # Documentação da configuração
│   ├── settings.json            # Config do projeto (commitar)
│   ├── settings.local.json      # Config local (NÃO commitar)
│   ├── skills/                  # Skills — expertise automatizada
│   │   ├── django-service-layer/
│   │   ├── pyspark-pipeline/
│   │   ├── unity-mobile/
│   │   ├── gitlab-cicd/
│   │   └── opentelemetry-instrumentation/
│   └── commands/                # Comandos customizados
│       ├── review-pr.md
│       ├── n1-audit.md
│       ├── check-migrations.md
│       └── dynatrace-check.md
│
├── tasks/                       # Gestão de tarefas
│   ├── todo.md                  # Tarefa ativa
│   ├── lessons.md               # Lições aprendidas
│   ├── decisions.md             # Architecture Decision Records
│   └── archive/                 # Tarefas concluídas
│
└── docs/                        # Documentação
    └── guia-claude-code.md      # Guia completo Claude Code
```

## 🚀 Quick Start

### 1. Instalação

```bash
# macOS
brew install claude-code@latest

# Linux / outros
# Ver https://code.claude.com/docs
```

### 2. Setup Inicial

```bash
# Clonar este repo (ou usar como template)
git clone <repo-url>
cd claude-md

# Copiar .env.example para .env
cp .env.example .env

# Editar .env com seus tokens/credenciais
# Preencher: GITLAB_TOKEN, POSTGRES_CONNECTION_STRING, INFISICAL_TOKEN, etc.
```

### 3. Primeiro Uso

```bash
# Iniciar Claude Code
claude

# Claude lerá automaticamente:
# - CLAUDE.md (instruções do projeto)
# - .claude/settings.json (configuração, hooks, MCP servers)
# - .claude/skills/ (expertise automatizada)
# - tasks/todo.md (contexto da última tarefa)
```

## 🧠 Skills Disponíveis

Skills são expertise automatizada que Claude carrega por contexto.

| Skill                          | Quando Usa                                      |
|--------------------------------|-------------------------------------------------|
| `django-service-layer`         | Criar/refatorar lógica Django com Service Layer |
| `pyspark-pipeline`             | Criar/otimizar pipelines PySpark/Airflow        |
| `unity-mobile`                 | Desenvolver features Unity Mobile Android       |
| `gitlab-cicd`                  | Configurar/otimizar pipelines GitLab CI/CD      |
| `opentelemetry-instrumentation`| Adicionar tracing/métricas com OpenTelemetry    |

**Como funciona:**

```
Você: "Preciso criar um service layer para pedidos"
Claude: [carrega django-service-layer skill automaticamente]
        [aplica padrão Protocol-based DI]
        [cria testes]
```

## 🎯 Comandos Customizados

Comandos são invocados manualmente com `/comando`.

| Comando              | Descrição                                        |
|----------------------|--------------------------------------------------|
| `/review-pr`         | Revisa PR atual (segurança + qualidade + padrões)|
| `/n1-audit`          | Analisa código Django para N+1 queries           |
| `/check-migrations`  | Verifica migrations pendentes e conflitos        |
| `/dynatrace-check`   | Consulta Dynatrace para métricas da aplicação    |

**Uso:**

```
/review-pr         # revisar PR
/n1-audit          # detectar N+1 queries
```

## 🪝 Hooks Configurados

Hooks executam automaticamente em eventos específicos.

| Evento                  | Hook                              | Propósito               |
|-------------------------|-----------------------------------|-------------------------|
| `SessionStart`          | `git status && git log -5`        | Mostrar contexto de git |
| `PostToolUse(Write(*.py))` | `ruff check && ruff format`    | Auto-format Python      |
| `PostToolUse(Edit(*.py))` | `ruff check && ruff format`     | Auto-format Python      |
| `PreToolUse(Bash(git commit*))` | `detect-secrets`           | Evitar commit de secrets|

## 🔗 MCP Servers Configurados

Model Context Protocol conecta Claude Code a ferramentas externas.

| Server       | Propósito                           | Escopo    |
|--------------|-------------------------------------|-----------|
| `memory`     | Persistência cross-session          | global    |
| `gitlab`     | PRs, issues, pipelines              | project   |
| `postgres`   | Queries, schema, migrations         | project   |
| `filesystem` | Acesso estruturado a arquivos       | project   |

**Configuração:** variáveis de ambiente no `.env`

## 📋 Workflow Recomendado

### 1. Iniciar Nova Tarefa

```bash
# Atualizar tasks/todo.md com nova tarefa
# Claude lerá automaticamente no bootstrap
claude
```

### 2. Desenvolvimento

```
"Preciso implementar autenticação via Keycloak"

Claude:
1. Lê CLAUDE.md (entende stack e padrões)
2. Carrega django-service-layer skill (se aplicável)
3. Cria service layer com Protocol-based DI
4. Escreve testes (TDD)
5. Auto-formata com ruff (hook PostToolUse)
6. Executa testes
```

### 3. Review

```
/review-pr

Claude revisa:
- Segurança (secrets, injection, auth)
- Performance (N+1, índices)
- Padrões (CLAUDE.md)
- Qualidade (lint, cobertura)
- Testes
```

### 4. Conclusão

```
1. Atualizar tasks/todo.md (marcar etapas concluídas)
2. Registrar lições em tasks/lessons.md (se houver)
3. Mover tasks/todo.md → tasks/archive/YYYY-MM-DD_nome.md
4. Criar PR
```

## 🎓 Stack Específica

### Python / Django / Vue.js

- **Gerenciador de pacotes:** UV (SEMPRE)
- **Lint:** Ruff + Mypy
- **Testes:** Pytest -n auto (paralelismo)
- **TDD:** Red → Green → Refactor (obrigatório)
- **DI:** Protocol-based (não herança)
- **Padrão:** Service Layer + Repository

**Ciclo de qualidade:**

```bash
ruff check . --fix && ruff format .
mypy .
pytest --cov -n auto
```

### PySpark / Airflow / Hadoop

- **NUNCA** `.collect()` sem amostragem
- **SEMPRE** broadcast joins para tabelas < 200MB
- **Validar** schema antes de transformações
- **DAGs** idempotentes por padrão

### C# / Unity (Mobile Android)

- **Build:** IL2CPP + ARM64
- **Renderização:** URP
- **Arquitetura:** MVC/MVP (sem singletons estáticos)
- **Performance:** Object Pooling, sem FindObjectOfType em Update
- **Testes:** Unity Test Framework (Edit + Play Mode)

## 💡 Prompt Caching (API)

Para uso via API Anthropic (não Claude Code CLI):

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-...")

# Bloco estável — cacheia
STABLE = open("CLAUDE.md").read()

messages = [{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": STABLE,
            "cache_control": {"type": "ephemeral"}  # CACHEIA
        },
        {
            "type": "text",
            "text": f"Tarefa: {user_input}"  # NÃO cacheia
        }
    ]
}]
```

**Economia:** ~80-85% de tokens em sessões longas.

## 🔒 Segurança

### ❌ NUNCA Commitar

- `.env`
- `.claude/settings.local.json`
- Tokens, API keys, credenciais
- Arquivos `.pem`, `.key`, `.p12`

### ✅ SEMPRE Commitar

- `CLAUDE.md`
- `.claude/settings.json` (sem tokens)
- `.claude/skills/`
- `.claude/commands/`
- `tasks/` (exceto dados sensíveis)

### Validação Automática

Hook `PreToolUse(Bash(git commit*))` detecta automaticamente arquivos suspeitos antes de commitar.

## 📚 Documentação

- **[CLAUDE.md](./CLAUDE.md)** — Instruções completas do projeto
- **[.claude/README.md](./.claude/README.md)** — Configuração detalhada
- **[docs/guia-claude-code.md](./docs/guia-claude-code.md)** — Guia completo Claude Code
- **[tasks/lessons.md](./tasks/lessons.md)** — Lições aprendidas
- **[tasks/decisions.md](./tasks/decisions.md)** — Architecture Decision Records

## 🆘 Troubleshooting

### Claude não carrega skill

- Verifique descrição da skill vs. contexto
- Mencione explicitamente: "Use a skill django-service-layer"

### Hook não executa

- Verifique matcher (`Write(*.py)` vs `Write(**/*.py)`)
- Use `claude --debug` para ver logs
- Verifique variáveis (`$CLAUDE_FILE_PATH`)

### MCP server não conecta

- Verifique `.env` (tokens, URLs)
- Teste manualmente: `npx @modelcontextprotocol/server-nome`
- Verifique logs: `claude --debug`

### Permissões repetitivas

- Adicione em `settings.json → permissions.allow`
- Use `/less-permission-prompts` para sugerir allowlist

## 🌟 Contribuindo

### Adicionar Nova Skill

```bash
mkdir -p .claude/skills/minha-skill
```

```markdown
<!-- .claude/skills/minha-skill/SKILL.md -->
---
name: minha-skill
description: Quando essa skill deve ser usada
---

# Minha Skill
[conteúdo]
```

### Adicionar Novo Comando

```markdown
<!-- .claude/commands/meu-comando.md -->
---
description: Breve descrição
---

[Prompt que Claude executará]
```

### Atualizar Lições

Sempre que aprender algo:

```markdown
<!-- tasks/lessons.md -->
### [PADRÃO] Descrição

**Contexto:** [...]
**Solução:** [...]
**Quando aplicar:** [...]
```

## 📞 Suporte

- **Claude Code Docs:** https://code.claude.com/docs
- **GitHub Issues:** https://github.com/anthropics/claude-code/issues
- **MCP Servers:** https://github.com/modelcontextprotocol/servers

---

**Versão:** 3.0  
**Última atualização:** 2026-05-14  
**Stack:** Python 3.12 | Django 6.x | PySpark 3.x | Unity 2022.3 LTS
