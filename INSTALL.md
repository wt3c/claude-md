# Instalação da Configuração Global do Claude Code

Este guia instala a configuração em `~/.claude/` nos dois ambientes.

---

## Linux (Garuda / Arch)

```bash
# 1. Criar diretório global do Claude Code
mkdir -p ~/.claude/skills
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/tasks/archive

# 2. Copiar CLAUDE.md global
cp CLAUDE.md ~/.claude/CLAUDE.md

# 3. Copiar settings.json global
cp settings.json ~/.claude/settings.json

# 4. Copiar skills
cp -r skills/* ~/.claude/skills/

# 5. Copiar commands
cp -r commands/* ~/.claude/commands/

# 6. Copiar templates de tasks (apenas se não existirem ainda)
[ ! -f ~/.claude/tasks/todo.md ] && cp tasks/todo.md ~/.claude/tasks/todo.md
[ ! -f ~/.claude/tasks/lessons.md ] && cp tasks/lessons.md ~/.claude/tasks/lessons.md
[ ! -f ~/.claude/tasks/decisions.md ] && cp tasks/decisions.md ~/.claude/tasks/decisions.md

# 7. Criar arquivo de auditoria
touch ~/.claude/audit.log

# 8. Verificar
ls ~/.claude/
```

---

## Windows 11 (PowerShell)

```powershell
# 1. Criar diretório global do Claude Code
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\commands"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\tasks\archive"

# 2. Copiar CLAUDE.md global
Copy-Item CLAUDE.md "$env:USERPROFILE\.claude\CLAUDE.md"

# 3. Copiar settings.json global
Copy-Item settings.json "$env:USERPROFILE\.claude\settings.json"

# 4. Copiar skills
Copy-Item -Recurse skills\* "$env:USERPROFILE\.claude\skills\"

# 5. Copiar commands
Copy-Item -Recurse commands\* "$env:USERPROFILE\.claude\commands\"

# 6. Copiar templates de tasks (apenas se não existirem)
if (-not (Test-Path "$env:USERPROFILE\.claude\tasks\todo.md")) {
    Copy-Item tasks\todo.md "$env:USERPROFILE\.claude\tasks\todo.md"
}

# 7. Criar arquivo de auditoria
New-Item -ItemType File -Force -Path "$env:USERPROFILE\.claude\audit.log"

# 8. Verificar
Get-ChildItem "$env:USERPROFILE\.claude\"
```

---

## Variáveis de Ambiente Obrigatórias

Adicionar ao `.bashrc` / `.zshrc` (Linux) ou Perfil PowerShell (Windows):

```bash
# Linux — ~/.bashrc ou ~/.zshrc
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_URL="https://gitlab-dti.mprj.mp.br"
export INFISICAL_TOKEN=""   # deixar vazio — preenchido pelo infisical login
export APP_ENV="dev"
```

```powershell
# Windows — $PROFILE
$env:GITLAB_TOKEN = "glpat-xxxxxxxxxxxxxxxxxxxx"
$env:GITLAB_URL = "https://gitlab-dti.mprj.mp.br"
$env:APP_ENV = "dev"
```

---

## MCP Servers — Configuração pós-instalação

```bash
# GitLab MPRJ (escopo local — não commitado)
claude mcp add --scope local gitlab -- npx -y @modelcontextprotocol/server-gitlab

# PostgreSQL local (escopo local)
claude mcp add --scope local postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:pass@localhost:5432/dev_db"

# Playwright (escopo de projeto — adicionar em cada projeto)
claude mcp add playwright npx @playwright/mcp@latest
```

---

## Atualização

Para atualizar a configuração global depois de mudar este repositório:

```bash
# Linux — re-executar o bloco de cópia
cp CLAUDE.md ~/.claude/CLAUDE.md
cp settings.json ~/.claude/settings.json
cp -r skills/* ~/.claude/skills/
cp -r commands/* ~/.claude/commands/
```
