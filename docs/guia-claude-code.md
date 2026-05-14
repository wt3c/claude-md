# Guia Completo: Claude Code — Do Zero ao Power User

> Guia passo a passo para developers backend sênior que querem dominar Claude Code como ferramenta de automação,
> arquitetura e fluxo de trabalho agentic.

---

## Índice

1. [O que é Claude Code — e o que ele não é](#1-o-que-é-claude-code)
2. [Instalação e primeiros passos](#2-instalação-e-primeiros-passos)
3. [Superfícies disponíveis (onde roda)](#3-superfícies-disponíveis)
4. [CLAUDE.md — A Constituição do Projeto](#4-claudemd)
5. [Slash Commands — Controle de sessão e atalhos](#5-slash-commands)
6. [Skills — Expertise automatizada por contexto](#6-skills)
7. [Hooks — Automação de ciclo de vida](#7-hooks)
8. [Subagentes e Agent Teams — Paralelismo e delegação](#8-subagentes-e-agent-teams)
9. [MCP (Model Context Protocol) — Integrações externas](#9-mcp)
10. [Configuração: settings.json e permissões](#10-configuração-settingsjson)
11. [Modo Headless / CI — Claude Code em pipelines](#11-modo-headless--ci)
12. [Routines / Scheduled Tasks — Agendamento](#12-routines--scheduled-tasks)
13. [Gestão de contexto e custo](#13-gestão-de-contexto-e-custo)
14. [Segurança e boas práticas](#14-segurança-e-boas-práticas)
15. [Roteiro de aprendizado progressivo](#15-roteiro-de-aprendizado-progressivo)

---

## 1. O que é Claude Code

Claude Code é uma **ferramenta de coding agentic** que roda no terminal (e em IDEs). Ele não é autocomplete de linha —
ele:

- Lê o projeto inteiro para ter contexto completo
- Planeja mudanças em múltiplos arquivos
- Executa comandos de shell, roda testes, itera em falhas
- Integra com git, GitHub/GitLab, Kubernetes, e qualquer CLI

**Diferença crucial:**

| Ferramenta       | Escopo            | Paradigma                     |
|------------------|-------------------|-------------------------------|
| Copilot / Cursor | Linha/bloco atual | Autocomplete                  |
| Claude Code      | Projeto inteiro   | Agente autônomo com aprovação |

O developer define o objetivo e revisa o resultado — não guia cada passo.

---

## 2. Instalação e Primeiros Passos

### Instalação (2025+)

```bash
# macOS — Homebrew (recomendado, não auto-atualiza)
brew install claude-code          # canal stable (~1 semana atrás)
brew install claude-code@latest   # último release imediato

# Linux (Garuda/Arch)
# Use o método direto via download — ver docs oficiais em code.claude.com/docs
```

> **Atenção:** Instalação via `npm install -g @anthropic-ai/claude-code` está **deprecated**. Use os métodos acima.

### Primeiro uso

```bash
cd meu-projeto
claude
```

Na primeira execução, ele pede autenticação (conta Anthropic ou API key). Depois disso, você está no prompt interativo.

### Flags essenciais do CLI

```bash
claude                          # modo interativo no diretório atual
claude -p "revise este código"  # modo headless/print (uma tarefa, sai)
claude --resume                 # retoma última sessão
claude --continue               # continua a sessão mais recente
claude --debug                  # logs detalhados (hooks, tool calls, timing)
claude --allowedTools "Read,Write"  # restringe ferramentas disponíveis
```

---

## 3. Superfícies Disponíveis

Claude Code roda em múltiplos ambientes:

| Superfície               | Como acessar          | Melhor para                               |
|--------------------------|-----------------------|-------------------------------------------|
| **Terminal CLI**         | `claude` no shell     | Uso diário principal                      |
| **VS Code**              | Extensão oficial      | Código + diff inline                      |
| **JetBrains**            | Plugin oficial        | IntelliJ, PyCharm, etc.                   |
| **Desktop App**          | Download em claude.ai | Interface visual + scheduled tasks locais |
| **Web App**              | claude.ai/code        | Acesso de qualquer lugar                  |
| **iOS (Remote Control)** | App Claude            | Supervisão mobile de agentes rodando      |
| **GitHub Actions**       | `/install-github-app` | CI/CD integrado ao PR workflow            |

---

## 4. CLAUDE.md

O `CLAUDE.md` é o arquivo mais importante do seu fluxo. **Claude lê ele no início de cada sessão.** É a "constituição"do
projeto.

### Hierarquia de localização

```
~/.claude/CLAUDE.md          # Global — aplica em TODOS os projetos
meu-projeto/CLAUDE.md        # Projeto — compartilhado com o time (commitar)
meu-projeto/.claude/CLAUDE.md  # Alternativa de localização de projeto
```

### Estrutura recomendada para um projeto Django/DRF

```markdown
# Projeto: Gatekeeper (Django + DRF + Vue.js 3)

## Stack

- Backend: Python 3.12, Django 5.x, Django REST Framework
- Frontend: Vue.js 3 + Vite
- Auth: Keycloak (OIDC)
- Deploy: OpenShift 4.14 (namespace: gatekeeper-prod)
- DB: PostgreSQL 15

## Comandos essenciais

- Build: `make build`
- Testes: `pytest -v --tb=short`
- Lint: `ruff check . && mypy src/`
- Migrations: `python manage.py migrate`

## Padrões de arquitetura

- Fat models → Services/Repositories (Protocol-based DI)
- Nunca lógica de negócio nas views
- Testes: characterization tests primeiro, depois refactor
- Identificadores: inglês; comentários: português

## Convenções de commit

- `feat(scope): descrição`
- `fix(scope): descrição`
- `chore(scope): descrição`

## O que NÃO fazer

- Não usar `select_related` sem verificar N+1 no Django Debug Toolbar
- Não commitar secrets ou API keys
- Não modificar migrations já aplicadas em produção
```

### Dicas de manutenção

- Mantenha abaixo de **~300 linhas** — se crescer demais, divida em arquivos por contexto
- Nunca coloque secrets, tokens ou senhas aqui
- Atualize sempre que arquitetura mudar
- Use `/init` para gerar um CLAUDE.md inicial automaticamente a partir do projeto

---

## 5. Slash Commands

Slash commands são **atalhos de sessão** que você invoca explicitamente com `/`.

### Categorias

#### Gestão de sessão

```
/clear          # limpa histórico da conversa
/compact        # comprime histórico em resumo (libera contexto — IRREVERSÍVEL na sessão)
/recap          # resume o que foi feito até agora (útil ao retornar)
/branch         # cria fork da conversa em nova sessão (era /fork)
/resume         # abre picker de sessões anteriores
```

#### Contexto e memória

```
/init           # gera CLAUDE.md para o projeto atual
/memory         # mostra/edita memória persistente do projeto
/config         # abre configuração interativa
```

#### Review e qualidade

```
/review         # revisão de código da sessão
/security-review  # auditoria de segurança
/bug            # reporta bug direto para Anthropic
```

#### Ferramentas e configuração

```
/model          # troca o modelo (Sonnet 4.6, Opus 4.7, etc.)
/effort         # ajusta nível de esforço do modelo
/mcp            # gerencia servidores MCP conectados
/sandbox        # ativa sandbox de filesystem/rede para bash
/status         # mostra modelo atual, contexto, sessão
/usage          # dashboard: uso, custo, rate limits, sessões
/terminal-setup # configura atalhos de teclado no terminal
```

#### Agendamento

```
/schedule       # cria ou gerencia scheduled tasks (routines)
/loop 5m /cmd   # repete um slash command em intervalo na sessão
```

### Criando seus próprios Slash Commands

```bash
# Comando de projeto (compartilhado com o time)
mkdir -p .claude/commands
cat > .claude/commands/review-pr.md << 'EOF'
---
description: Revisa o PR atual para qualidade, segurança e padrões do projeto
---
Revise o diff atual considerando:
1. Segurança (injection, auth, data exposure)
2. Performance (N+1, índices ausentes, queries desnecessárias)
3. Padrões definidos no CLAUDE.md
4. Cobertura de testes

Retorne um relatório estruturado com: CRÍTICO / ATENÇÃO / SUGESTÃO
EOF

# Comando pessoal (todos os seus projetos)
mkdir -p ~/.claude/commands
echo "Analise este código Django para N+1 queries e sugira select_related/prefetch_related" \
  > ~/.claude/commands/n1-audit.md
```

> **Nota:** Arquivos em `.claude/commands/` ainda funcionam, mas a abordagem recomendada atual é usar **Skills** (
`.claude/skills/`). Skills suportam tudo que comandos fazem + auto-invocação por contexto.

---

## 6. Skills

Skills são guias em Markdown que ensinam Claude a lidar com **tarefas específicas**. A diferença chave dos Slash
Commands:

|             | Slash Command                      | Skill                            |
|-------------|------------------------------------|----------------------------------|
| Invocação   | Você chama explicitamente (`/cmd`) | Claude decide usar pelo contexto |
| Quando usar | Quer controle do timing            | Quer expertise automática        |

### Estrutura de uma Skill

```bash
mkdir -p .claude/skills/django-service-layer
cat > .claude/skills/django-service-layer/SKILL.md << 'EOF'
---
name: django-service-layer
description: >
  Aplicar o padrão Service/Repository com Protocol-based DI
  em código Django/DRF. Usar quando criar ou refatorar views,
  serializers ou models que contêm lógica de negócio.
---

# Django Service Layer Pattern

## Quando aplicar
- View contém lógica de negócio
- Model tem métodos além de save/clean
- Lógica duplicada entre views/tasks

## Estrutura alvo
```

apps/
minha_app/
models.py # apenas dados e validação simples
services.py # lógica de negócio
repositories.py # acesso a dados (Protocol)
views.py # apenas orquestração HTTP

```

## Protocolo base
```python
from typing import Protocol

class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User: ...
    def save(self, user: User) -> User: ...
```

## Regras

- Nunca importar `request` dentro de services
- Services recebem dados puros, não objetos HTTP
- Repository sempre recebe e retorna domain objects
  EOF

### Skill vs CLAUDE.md

- **CLAUDE.md** → contexto estático que raramente muda (stack, comandos, padrões gerais)
- **Skill** → expertise especializada e reutilizável que Claude aplica dinamicamente

---

## 7. Hooks

Hooks são **comandos shell, HTTP endpoints ou prompts de LLM** que rodam automaticamente em pontos específicos do ciclo
de vida do Claude Code.

### Eventos disponíveis

| Evento               | Quando dispara                |
|----------------------|-------------------------------|
| `SessionStart`       | Início ou retomada de sessão  |
| `PreToolUse`         | Antes de qualquer tool call   |
| `PostToolUse`        | Depois de tool call (sucesso) |
| `PostToolUseFailure` | Depois de tool call (falha)   |
| `PermissionRequest`  | Quando Claude pede permissão  |
| `PermissionDenied`   | Permissão negada              |
| `FileChanged`        | Arquivo do projeto alterado   |
| `Notification`       | Mudança de status             |

### Configuração em `.claude/settings.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check \"$CLAUDE_FILE_PATH\" --fix && mypy \"$CLAUDE_FILE_PATH\""
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash(*)",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[Hook] Bash: $CLAUDE_TOOL_INPUT\" >> ~/.claude/audit.log"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "git log --oneline -5 && echo '---' && git status --short"
          }
        ]
      }
    ]
  }
}
```

### Casos de uso práticos para seu stack

```bash
# Auto-format Python após cada escrita
"Write(*.py)" → "ruff format \"$CLAUDE_FILE_PATH\""

# Rodar testes afetados após mudança
"Write(apps/**/*.py)" → "pytest --testpaths=$(dirname $CLAUDE_FILE_PATH) -q"

# Bloquear commits com secrets
"Bash(git commit*)" → "./scripts/detect-secrets.sh"

# Log de auditoria de comandos Bash (útil em OpenShift CI)
"Bash(*)" → "echo \"$(date): $CLAUDE_TOOL_INPUT\" >> audit.log"

# MCP tools seguem o padrão: mcp__<server>__<tool>
"mcp__memory__.*" → "echo 'Atualizando memória do projeto'"
```

> **Variáveis disponíveis nos hooks:**
> - `$CLAUDE_FILE_PATH` — arquivo afetado
> - `$CLAUDE_TOOL_INPUT` — input do tool call
> - `$CLAUDE_TOOL_NAME` — nome da ferramenta

---

## 8. Subagentes e Agent Teams

### Subagentes (Task tool)

Permite que Claude delegue uma subtarefa para um agente isolado, evitando poluição do contexto principal.

```
Use um subagente para explorar o módulo de autenticação e retorne
um resumo da lógica de permissões, sem trazer todo o código.
```

**Quando usar:**

- Exploração profunda de código sem poluir contexto
- Tarefas paralelas independentes
- Análise de múltiplos módulos simultaneamente

### Agent Teams (v2.1.32+)

```
Coordene 3 agentes em paralelo:
- Agente 1: auditoria de segurança em apps/auth/
- Agente 2: análise de N+1 em apps/api/
- Agente 3: revisão de migrations pendentes
Consolide os resultados em um relatório único.
```

**Árvore de decisão:**

```
Precisa de contexto isolado?
├── SIM → É uma ou várias subtarefas?
│         ├── UMA → Subagente (Task tool)
│         └── VÁRIAS → Agent Team
└── NÃO → Claude principal resolve diretamente
```

---

## 9. MCP

O **Model Context Protocol** é o padrão aberto que conecta Claude Code a ferramentas e fontes de dados externas.

### Adicionando servidores

```bash
# Via CLI (salva em .claude/settings.json por padrão — projeto)
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# Via SSE transport (serviços internos)
claude mcp add --transport sse minha-api https://api.mprj.internal/mcp

# Escopo global (todos os projetos)
claude mcp add --scope global meu-server -- npx meu-mcp-server

# Escopo local (não compartilhado com o time)
claude mcp add --scope local keycloak-admin -- python keycloak_mcp.py
```

### Escopos de configuração

| Escopo             | Arquivo                       | Compartilhado?             |
|--------------------|-------------------------------|----------------------------|
| `project` (padrão) | `.claude/settings.json`       | ✅ commitado no git         |
| `local`            | `.claude/settings.local.json` | ❌ pessoal                  |
| `global`           | `~/.claude/settings.json`     | ❌ todos os projetos locais |

### Servidores úteis para seu stack

```bash
# GitHub — PRs, issues, code review
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# Filesystem estruturado
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /workspace

# PostgreSQL (seu banco Django)
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:pass@localhost:5432/gatekeeper"

# Playwright (testes E2E)
claude mcp add playwright npx @playwright/mcp@latest

# Memory (persistência cross-session)
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
```

### Usando ferramentas MCP na sessão

```bash
# Ferramentas MCP aparecem como slash commands:
/mcp__github__list_prs
/mcp__github__create_pr
/mcp__postgres__query

# Ou naturalmente no prompt:
"Liste os PRs abertos no repositório gatekeeper-backend"
"Consulte a tabela users e mostre os 10 últimos registros"
```

> **Otimização de contexto:** Claude Code não carrega os schemas completos de todos os MCP tools no startup. Ele carrega
> apenas os nomes e busca o schema completo on-demand (ToolSearch). Isso reduz muito o overhead de contexto com
> múltiplos
> servidores.

---

## 10. Configuração: settings.json

O arquivo `.claude/settings.json` centraliza permissões, hooks, MCP e comportamentos.

### Estrutura completa

```json
{
  "model": "claude-sonnet-4-6",
  "allowedTools": [
    "Read",
    "Write",
    "Bash",
    "mcp__github__.*"
  ],
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(pytest *)",
      "Bash(ruff *)",
      "Bash(mypy *)",
      "Write(src/**/*)",
      "Write(tests/**/*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Write(/etc/*)"
    ]
  },
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check \"$CLAUDE_FILE_PATH\" --fix"
          }
        ]
      }
    ]
  }
}
```

### Pre-aprovação de comandos comuns

Reduz drasticamente os prompts de permissão:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(pytest *)",
      "Bash(python manage.py *)",
      "Bash(make *)"
    ]
  }
}
```

> Use `/less-permission-prompts` para que Claude Code analise seu histórico e sugira automaticamente um allowlist
> otimizado.

---

## 11. Modo Headless / CI

Claude Code pode rodar de forma não-interativa em pipelines.

### Básico

```bash
# Executa uma tarefa e sai
claude -p "revise o PR #42 e retorne um relatório JSON"

# Output estruturado para parsing
claude -p "analise os testes falhando" --output-format json

# Limitar ferramentas em ambiente CI (segurança)
claude -p "rode os testes e relate falhas" --allowedTools "Read,Bash(pytest *)"
```

### GitHub Actions

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review
on: [ pull_request ]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Code Review
        run: |
          claude -p "Revise este PR para segurança, qualidade e conformidade com CLAUDE.md" \
            --allowedTools "Read" \
            --output-format json > review.json
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Pipeline com pipe

```bash
# Analisar logs
tail -200 app.log | claude -p "identifique anomalias e erros críticos"

# Revisão de segurança em arquivos modificados
git diff main --name-only | claude -p "revise estes arquivos para vulnerabilidades"

# Bulk operations
find . -name "*.py" -newer last_audit | \
  claude -p "audite estes arquivos Python para compliance PEP8 e type hints"
```

---

## 12. Routines / Scheduled Tasks

Routines são **cron jobs gerenciados pela Anthropic** que rodam Claude Code na nuvem, mesmo com seu computador
desligado.

### Criar uma routine

```bash
# Via CLI
claude trigger create \
  --schedule "0 9 * * 1" \
  --prompt "Revise os PRs abertos, identifique os bloqueados há mais de 2 dias e crie um resumo"

# Via slash command na sessão
/schedule
```

### Casos de uso

```
Toda segunda 9h:  Revisar PRs abertos e gerar relatório de status
Diariamente 8h:   Analisar logs de produção da última noite
Toda sexta 17h:   Gerar changelog semanal a partir dos commits
A cada merge:     Atualizar documentação afetada (trigger via GitHub webhook)
```

### Desktop Scheduled Tasks

Criadas via Desktop App — rodam **na sua máquina**, com acesso direto a arquivos e ferramentas locais (útil para tarefas
que precisam de acesso ao filesystem ou ferramentas locais do MPRJ).

---

## 13. Gestão de Contexto e Custo

### Princípios

- Claude Code é **stateless entre sessões** — o CLAUDE.md carrega o contexto estático
- Dentro de uma sessão, o histórico cresce — gerencie ativamente
- Token costs acumulam rápido com subagentes e MCP verboso

### Comandos de gestão de contexto

```
/compact    # Comprime histórico em resumo (IRREVERSÍVEL na sessão — salve antes)
/clear      # Limpa tudo — começa fresh
/branch     # Bifurca sessão para explorar sem poluir o principal
/usage      # Veja consumo, custo e rate limits em tempo real
```

### Boas práticas de custo

```
✅ Use /compact em sessões longas antes que o contexto estoure
✅ Salve contexto crítico no CLAUDE.md ANTES de /compact
✅ Use subagentes para exploração — não traz todo o código pro contexto principal
✅ Prefira --allowedTools restrito em tarefas simples
✅ Use headless mode (-p) para tarefas únicas e repetitivas
✅ Revise o schema de MCP servers — schemas verbosos custam tokens no startup
❌ Nunca use Bash(*) como allowlist — autoriza qualquer comando
❌ Não coloque documentação extensa no CLAUDE.md — use Skills
```

### Rate limits (2026)

- Limits são **semanais** para subscribers pagos
- Max subscribers podem comprar usage adicional além do limite
- `/usage` mostra o estado atual em tempo real

---

## 14. Segurança e Boas Práticas

### Permissões

```json
// ❌ NUNCA faça isso
{
  "permissions": {
    "allow": [
      "Bash(*)"
    ]
  }
}

// ✅ Seja específico
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(pytest *)"
    ]
  }
}
```

### Secrets e credenciais

```bash
# ❌ Nunca coloque em CLAUDE.md ou no chat
KEYCLOAK_SECRET=abc123

# ✅ Use variáveis de ambiente nos MCP servers
"env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
```

### Modelo de confiança

- Por padrão, Claude Code **pede aprovação** antes de modificar arquivos ou rodar comandos
- Use `/sandbox` para limitar escrita e rede em sessões exploratórias
- Claude Code só escreve na pasta onde foi iniciado e subpastas
- Revise **sempre o diff** antes de aceitar mudanças — `diff mode` é seu aliado

### Em ambientes corporativos (MPRJ/OpenShift)

```bash
# Escopo local para configs sensíveis (não commitar)
claude mcp add --scope local keycloak-admin -- python keycloak_mcp.py

# Audit log via hook
{
  "PreToolUse": [{
    "matcher": "Bash(*)",
    "hooks": [{"type": "command", "command": "echo \"$(date): $CLAUDE_TOOL_INPUT\" >> ~/.claude/audit.log"}]
  }]
}
```

---

## 15. Roteiro de Aprendizado Progressivo

### Semana 1 — Fundação

- [ ] Instalar Claude Code no Garuda Linux
- [ ] Rodar `claude` em um projeto existente (Gatekeeper, por exemplo)
- [ ] Usar `/init` para gerar CLAUDE.md inicial
- [ ] Refinar o CLAUDE.md com stack, comandos e padrões reais
- [ ] Aprender: `/clear`, `/compact`, `/status`, `/model`
- [ ] Praticar: pedir uma refatoração simples e revisar o diff

### Semana 2 — Produtividade

- [ ] Criar 3-5 slash commands para tarefas repetitivas do seu dia (`/review-pr`, `/n1-audit`, `/check-migrations`)
- [ ] Configurar `permissions.allow` no `settings.json` para eliminar confirmações frequentes
- [ ] Adicionar hook `PostToolUse` para auto-format Python (`ruff format`)
- [ ] Experimentar `/security-review` em um módulo real

### Semana 3 — Integração

- [ ] Adicionar MCP server do GitHub (`/install-github-app` ou `claude mcp add github`)
- [ ] Adicionar MCP server do PostgreSQL apontando para banco local do projeto
- [ ] Testar: pedir ao Claude Code para criar um PR com as mudanças da sessão
- [ ] Criar uma Skill para o padrão Service/Repository do Django

### Semana 4 — Automação e Agência

- [ ] Criar uma Routine semanal (revisão de PRs ou análise de logs)
- [ ] Experimentar subagentes: delegar análise de módulo específico
- [ ] Usar modo headless em um pipeline GitLab CI local
- [ ] Construir um hook `SessionStart` que carrega contexto do sprint atual (git log + issues abertas)

### Semana 5+ — Power User

- [ ] Criar MCP server customizado para integração com APIs internas do MPRJ (Keycloak Admin API)
- [ ] Configurar Agent Team para revisão paralela de múltiplos módulos
- [ ] Dominar `/usage` e otimizar custo de tokens
- [ ] Contribuir com CLAUDE.md de stack específico (PySpark, OpenShift) como Skills reutilizáveis

---

## Referências

- **Docs oficiais:** https://code.claude.com/docs
- **GitHub (changelog):** https://github.com/anthropics/claude-code
- **MCP servers:** https://github.com/modelcontextprotocol/servers
- **Guia da comunidade:** https://github.com/FlorianBruniaux/claude-code-ultimate-guide
- **Cheatsheet de comandos:** https://www.scriptbyai.com/claude-code-commands-cheat-sheet/

---

*Última atualização do guia: Maio 2026 — baseado no Claude Code v2.1.x e Claude Sonnet 4.6*
