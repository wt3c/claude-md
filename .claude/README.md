# Claude Code — Configuração do Projeto

Este diretório contém toda a configuração do Claude Code para este projeto.

## 📁 Estrutura

```
.claude/
├── README.md              # Este arquivo
├── settings.json          # Configuração principal (commitar)
├── settings.local.json    # Configuração local (não commitar)
├── skills/                # Skills — expertise automatizada
│   ├── django-service-layer/
│   ├── pyspark-pipeline/
│   ├── unity-mobile/
│   ├── gitlab-cicd/
│   └── opentelemetry-instrumentation/
└── commands/              # Comandos customizados (slash commands)
    ├── review-pr.md
    ├── n1-audit.md
    ├── check-migrations.md
    └── dynatrace-check.md
```

## 🔧 Configuração

### settings.json (Projeto)

Configuração compartilhada com o time. **Commitar no git.**

**Conteúdo:**
- Hooks (auto-format, testes, validações)
- Permissões pré-aprovadas
- MCP servers (exceto tokens)
- Modelo padrão

### settings.local.json (Local)

Configuração pessoal. **NÃO commitar** (já no .gitignore).

**Conteúdo:**
- Tokens e credenciais pessoais
- Preferências individuais
- Overrides locais

**Exemplo:**

```json
{
  "mcpServers": {
    "infisical": {
      "command": "npx",
      "args": ["-y", "@infisical/mcp-server"],
      "env": {
        "INFISICAL_TOKEN": "st.xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## 🧠 Skills

Skills são expertise automatizada que Claude carrega por contexto.

### Disponíveis

| Skill                          | Quando Usa                                      |
|--------------------------------|-------------------------------------------------|
| `django-service-layer`         | Criar/refatorar lógica Django com Service Layer |
| `pyspark-pipeline`             | Criar/otimizar pipelines PySpark/Airflow        |
| `unity-mobile`                 | Desenvolver features Unity Mobile Android       |
| `gitlab-cicd`                  | Configurar/otimizar pipelines GitLab CI/CD      |
| `opentelemetry-instrumentation`| Adicionar tracing/métricas com OpenTelemetry    |

### Como Funciona

Claude carrega skills automaticamente quando o contexto da conversa se encaixa na descrição da skill. Você não precisa invocar manualmente (mas pode).

**Exemplo:**

```
Você: "Preciso criar um service layer para a lógica de pedidos"
Claude: [carrega django-service-layer skill automaticamente]
        [aplica padrão Protocol-based DI]
```

### Criar Nova Skill

```bash
mkdir -p .claude/skills/minha-skill
```

```markdown
<!-- .claude/skills/minha-skill/SKILL.md -->
---
name: minha-skill
description: >
  Descrição de quando essa skill deve ser usada.
  Claude usa isso para decidir se carrega automaticamente.
---

# Minha Skill

## Quando aplicar
[...]

## Padrões
[...]

## Exemplos
[...]
```

## 🎯 Comandos Customizados

Comandos são invocados manualmente com `/comando`.

### Disponíveis

| Comando              | Descrição                                        |
|----------------------|--------------------------------------------------|
| `/review-pr`         | Revisa PR atual (segurança + qualidade + padrões)|
| `/n1-audit`          | Analisa código Django para N+1 queries           |
| `/check-migrations`  | Verifica migrations pendentes e conflitos        |
| `/dynatrace-check`   | Consulta Dynatrace para métricas da aplicação    |

### Usar um Comando

```
/review-pr
```

Claude executará o prompt definido no arquivo `.claude/commands/review-pr.md`.

### Criar Novo Comando

```markdown
<!-- .claude/commands/meu-comando.md -->
---
description: Breve descrição do comando
---

[Prompt que Claude executará quando você usar /meu-comando]
```

**Diferença entre Skills e Comandos:**

- **Skill:** Claude decide quando usar (automático)
- **Comando:** Você invoca explicitamente (manual)

## 🔗 MCP Servers

Model Context Protocol conecta Claude Code a ferramentas externas.

### Configurados

| Server       | Propósito                           | Escopo    |
|--------------|-------------------------------------|-----------|
| `memory`     | Persistência cross-session          | global    |
| `gitlab`     | PRs, issues, pipelines              | project   |
| `postgres`   | Queries, schema, migrations         | project   |
| `filesystem` | Acesso estruturado a arquivos       | project   |

### Variáveis de Ambiente Necessárias

```bash
# .env (criar na raiz do projeto)
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_API_URL=https://gitlab-dti.mprj.mp.br/api/v4
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db
```

### Adicionar Novo MCP Server

```bash
# Via CLI (escopo project — commitar)
claude mcp add nome-server -- npx -y @modelcontextprotocol/server-nome

# Via CLI (escopo local — não commitar)
claude mcp add --scope local nome-server -- npx -y @modelcontextprotocol/server-nome

# Manual: editar .claude/settings.json ou .claude/settings.local.json
```

## 🪝 Hooks

Hooks executam automaticamente em eventos específicos.

### Configurados

| Evento                  | Hook                              | Propósito               |
|-------------------------|-----------------------------------|-------------------------|
| `SessionStart`          | `git status && git log -5`        | Mostrar contexto de git |
| `PostToolUse(Write(*.py))` | `ruff check && ruff format`    | Auto-format Python      |
| `PostToolUse(Edit(*.py))` | `ruff check && ruff format`     | Auto-format Python      |
| `PreToolUse(Bash(git commit*))` | `detect-secrets`           | Evitar commit de secrets|

### Variáveis Disponíveis em Hooks

- `$CLAUDE_FILE_PATH` — arquivo afetado
- `$CLAUDE_TOOL_INPUT` — input do tool call
- `$CLAUDE_TOOL_NAME` — nome da ferramenta

### Adicionar Novo Hook

Editar `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(tests/**/*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "pytest \"$CLAUDE_FILE_PATH\" -v"
          }
        ]
      }
    ]
  }
}
```

## 🚀 Quick Start

### 1. Primeira Vez

```bash
# Instalar Claude Code (se ainda não tiver)
brew install claude-code@latest  # macOS
# ou baixar de code.claude.com/docs

# Copiar .env.example para .env e preencher
cp .env.example .env
# Editar .env com seus tokens
```

### 2. Iniciar Sessão

```bash
cd seu-projeto
claude
```

Claude lerá automaticamente:
- `CLAUDE.md` (instruções do projeto)
- `.claude/settings.json` (configuração)
- `.claude/skills/` (expertise)
- `.claude/commands/` (comandos customizados)

### 3. Usar Comandos

```
/review-pr         # revisar PR atual
/n1-audit          # detectar N+1 queries
/check-migrations  # verificar migrations
/dynatrace-check   # consultar Dynatrace
```

### 4. Deixar Claude Trabalhar

```
"Preciso criar um service layer para pedidos"
→ Claude carrega django-service-layer skill
→ Aplica padrão Protocol-based DI
→ Cria testes

"Otimize este job Spark"
→ Claude carrega pyspark-pipeline skill
→ Sugere broadcast joins, particionamento, etc.
```

## 📚 Recursos

- [CLAUDE.md](../CLAUDE.md) — Instruções completas do projeto
- [tasks/](../tasks/) — Tarefas, lições, decisões
- [docs/guia-claude-code.md](../docs/guia-claude-code.md) — Guia completo

## 🔒 Segurança

### ❌ NUNCA Commitar

- `.claude/settings.local.json`
- `.env`
- Tokens, API keys, credenciais

### ✅ SEMPRE Commitar

- `.claude/settings.json` (sem tokens)
- `.claude/skills/`
- `.claude/commands/`
- `CLAUDE.md`
- `tasks/`

### Validação Pré-Commit

O hook `PreToolUse(Bash(git commit*))` detecta automaticamente arquivos suspeitos (`.env`, `.key`, `.pem`) antes de commitar.

## 🆘 Troubleshooting

### Claude não carrega skill automaticamente

- Verifique se a descrição da skill corresponde ao contexto
- Tente mencionar explicitamente: "Use a skill django-service-layer"

### Hook não executa

- Verifique o matcher (ex: `Write(*.py)` vs `Write(**/*.py)`)
- Use `claude --debug` para ver hooks sendo disparados
- Verifique variáveis de ambiente (`$CLAUDE_FILE_PATH`)

### MCP server não conecta

- Verifique variáveis de ambiente (.env)
- Teste o servidor manualmente: `npx @modelcontextprotocol/server-nome`
- Verifique logs: `claude --debug`

### Permissão negada repetidamente

- Adicione padrão em `settings.json → permissions.allow`
- Use `/less-permission-prompts` para sugerir allowlist automaticamente

## 📞 Suporte

- **Docs:** https://code.claude.com/docs
- **GitHub:** https://github.com/anthropics/claude-code/issues
- **Guia Interno:** [docs/guia-claude-code.md](../docs/guia-claude-code.md)
