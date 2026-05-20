# Instalação e Configuração do Claude Code

Guia completo para instalação da configuração global e setup de múltiplas contas (MPRJ/Foundry + pessoal PRO).

**Ambientes suportados:**
- **Linux** (Garuda/Arch, Ubuntu, etc.)
- **macOS**
- **Windows 11** (PowerShell)

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Instalação Rápida](#2-instalação-rápida)
3. [Configuração do Infisical](#3-configuração-do-infisical)
4. [Token GitLab](#4-token-gitlab)
5. [MCP Servers Adicionais](#5-mcp-servers-adicionais)
6. [Atualização](#6-atualização)
7. [Teclado ThinkPad T14 Gen 2i — ABNT2](#7-teclado-thinkpad-t14-gen-2i--abnt2)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Pré-requisitos

| Ferramenta | Versão Mínima | Instalação |
|------------|---------------|------------|
| **Python** | 3.12.10 | Gerenciado automaticamente por `uv` |
| **UV** | latest | [astral.sh/uv](https://astral.sh/uv) |
| **Git** | qualquer | [git-scm.com](https://git-scm.com) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) ou `nvm install --lts` |
| **Claude Code** | latest | `npm install -g @anthropic-ai/claude-code` |

### Instalar UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### Verificar instalação

```bash
uv --version
git --version
node --version    # v18+ requerido
claude --version
```

---

## 2. Instalação Rápida

### 2.1. Clonar o Repositório

```bash
# Linux/macOS
cd ~/workspace
git clone https://gitlab-dti.mprj.mp.br/seu-usuario/claude-md.git
cd claude-md

# Windows
cd D:\workspace
git clone https://gitlab-dti.mprj.mp.br/seu-usuario/claude-md.git
cd claude-md
```

### 2.2. Configurar Infisical (Opcional)

Se você deseja configuração automática de API keys via Infisical:

```bash
cp .env.example .env
# Edite .env com suas credenciais (veja seção 3)
```

**Nota**: Instalação sem Infisical é válida — você pode configurar API keys manualmente depois.

### 2.3. Executar o Instalador

#### Instalação Interativa (Recomendado)

```bash
uv run python install.py
```

O instalador irá:
1. ✅ Verificar pré-requisitos (Git, Node.js, Claude Code)
2. ✅ Criar backup de secrets existentes (`~/.claude-md-backups/`)
3. ✅ Configurar 3 ambientes: `~/.claude/`, `~/.claude-mprj/`, `~/.claude-pessoal/`
4. ✅ Instalar `CLAUDE.md`, `settings.json`, `skills/`, `commands/`
5. ✅ Configurar shell (bash/zsh/fish/PowerShell)
6. ✅ Instalar MCP servers globais (filesystem, memory, gitlab, postman)
7. ✅ Configurar API keys via Infisical (se disponível)

#### Instalação Não-Interativa (CI/CD)

```bash
uv run python install.py --non-interactive --multi-account
```

#### Apenas Atualizar Arquivos (Preserva Configs)

```bash
uv run python install.py --update-only
```

#### Apenas Instalar MCPs

```bash
uv run python install.py --mcps-only
```

### 2.4. Recarregar Shell

```bash
# Bash/Zsh
source ~/.bashrc  # ou ~/.zshrc

# Fish
source ~/.config/fish/config.fish

# PowerShell
. $PROFILE
```

### 2.5. Verificar Instalação

```bash
# Testar funções shell criadas
claude-mprj --version
claude-pro --version

# Listar MCPs instalados
claude mcp list
```

---

## 3. Configuração do Infisical

O Infisical gerencia secrets de forma centralizada e segura. O instalador pode configurar automaticamente:
- `ANTHROPIC_FOUNDRY_API_KEY` (MPRJ)
- `GITLAB_TOKEN` (GitLab DTI)
- `POSTMAN_API_KEY` (Postman)

### 3.1. Criar Projeto no Infisical

1. Acesse `https://ncd-infisical.mprj.mp.br/`
2. Crie um novo projeto (ex: "claude-config")
3. Use o environment `prod` (padrão)

### 3.2. Criar Machine Identity (Universal Auth)

1. **Organization Settings → Access Control → Machine Identities**
2. **Create Identity** → escolha **Universal Auth**
3. Copie:
   - `Client ID`
   - `Client Secret`
4. Adicione a identity ao projeto com permissões de **leitura**

### 3.3. Adicionar Secrets no Projeto

Em **Project → Secrets → prod**:

```bash
ANTHROPIC_FOUNDRY_API_KEY=sk-ant-api03-...
GITLAB_TOKEN=glpat-...
POSTMAN_API_KEY=PMAK-...
```

### 3.4. Configurar `.env` Local

Copie o template e preencha:

```bash
cp .env.example .env
```

Edite `.env`:

```dotenv
# Infisical Connection (não commitar!)
INFISICAL_CLIENT_ID=<seu-client-id>
INFISICAL_CLIENT_SECRET=<seu-client-secret>
INFISICAL_PROJECT_ID=767794c3-84e4-4ecb-b763-38c5d824f5c7
INFISICAL_SITE_URL=https://ncd-infisical.mprj.mp.br/
INFISICAL_ENVIRONMENT_SLUG=prod
```

**Importante**: `.env` já está no `.gitignore` — nunca comitar!

### 3.5. Instalação sem Infisical

Se você não tem acesso ao Infisical, configure manualmente:

#### API Key MPRJ (Foundry)

```bash
# Linux/macOS
mkdir -p ~/.secrets
echo "sk-ant-api03-..." > ~/.secrets/claude-mprj.key
chmod 600 ~/.secrets/claude-mprj.key

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.secrets"
Set-Content "$env:USERPROFILE\.secrets\claude-mprj.key" "sk-ant-api03-..."
```

#### GitLab Token

Adicione ao seu shell profile:

```bash
# Bash/Zsh (~/.bashrc ou ~/.zshrc)
export GITLAB_TOKEN="glpat-..."
export GITLAB_URL="https://gitlab-dti.mprj.mp.br"

# Fish (~/.config/fish/conf.d/gitlab.fish)
set -x GITLAB_TOKEN "glpat-..."
set -x GITLAB_URL "https://gitlab-dti.mprj.mp.br"

# PowerShell ($PROFILE)
$env:GITLAB_TOKEN = "glpat-..."
$env:GITLAB_URL = "https://gitlab-dti.mprj.mp.br"
```

---

## 4. Token GitLab

Obtenha seu token em: `https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens`

### Configurações Recomendadas

| Campo | Valor |
|-------|-------|
| **Token name** | `claude-code-mprj` |
| **Expiration** | 1 ano |
| **Scopes** | `api`, `read_repository`, `write_repository` |

### Scopes Explicados

| Scope | Necessário | Motivo |
|-------|------------|--------|
| `api` | ✅ | Acesso completo à API REST (projetos, MRs, issues, pipelines) |
| `read_repository` | ✅ | Clonar repos privados via HTTPS |
| `write_repository` | ✅ | Push via HTTPS |
| `read_registry` | ⚠️ | Apenas se usar Container Registry |
| `write_registry` | ⚠️ | Apenas se fazer push de imagens |

> **Importante**: Guardar o token em local seguro — o GitLab exibe apenas uma vez.

---

## 5. MCP Servers Adicionais

O instalador já configura automaticamente:
- ✅ `filesystem` — Acesso estruturado a arquivos
- ✅ `memory` — Persistência cross-session
- ✅ `gitlab` — Issues, MRs, pipelines
- ✅ `postman` — Collections, APIs

### PostgreSQL (Opcional)

Para adicionar acesso ao banco de dados:

```bash
# Conta MPRJ
CLAUDE_CONFIG_DIR=~/.claude-mprj claude mcp add --scope user postgres -- \
  npx -y @modelcontextprotocol/server-postgres \
  "postgresql://USER:PASS@HOST:5432/DATABASE"

# Conta Pessoal
CLAUDE_CONFIG_DIR=~/.claude-pessoal claude mcp add --scope user postgres -- \
  npx -y @modelcontextprotocol/server-postgres \
  "postgresql://USER:PASS@HOST:5432/DATABASE"
```

### Playwright (Por Projeto)

Para testes E2E em um projeto específico:

```bash
cd /caminho/do/projeto
claude mcp add --scope project playwright -- npx @playwright/mcp@latest
```

### Verificar MCPs Instalados

```bash
# Lista MCPs de todas as contas
claude mcp list

# Conta específica
CLAUDE_CONFIG_DIR=~/.claude-mprj claude mcp list
```

---

## 6. Atualização

### Atualizar Arquivos de Configuração

```bash
cd ~/workspace/claude-md  # ou D:\workspace\claude-md no Windows
git pull origin main
uv run python install.py --update-only
```

Isso atualiza:
- ✅ `CLAUDE.md`
- ✅ `settings.json`
- ✅ `skills/`
- ✅ `commands/`

**Preserva**:
- 🔒 `.mcp.json` (pode ter senhas)
- 🔒 `settings.local.json`
- 🔒 `tasks/*.md` (histórico do usuário)
- 🔒 Secrets e API keys

### Reinstalação Completa

Para refazer toda a configuração:

```bash
# 1. Backup manual (opcional)
cp -r ~/.claude-mprj ~/.claude-mprj.backup
cp -r ~/.claude-pessoal ~/.claude-pessoal.backup

# 2. Remover configuração antiga
python uninstall.py

# 3. Reinstalar
uv run python install.py
```

---

## 7. Teclado ThinkPad T14 Gen 2i — ABNT2

**Contexto**: Garuda Linux + Hyprland + Teclado ABNT2 físico

### Problema

A tecla <kbd>Ctrl Direito</kbd> não produz `/` e `?` como esperado no layout ABNT2.

### Solução: keyd + XKB Custom

O Hyprland intercepta modificadores antes do XKB, então precisamos:
1. **keyd** converte `rightcontrol` → keycode neutro (`102nd` = `<LSGT>`)
2. **XKB custom** mapeia `<LSGT>` → `/` e `?`

#### 1. Instalar keyd

```bash
sudo pacman -S keyd
sudo systemctl enable --now keyd
```

#### 2. Configurar keyd

Crie `/etc/keyd/default.conf`:

```ini
[ids]
*

[main]
rightcontrol = 102nd
```

```bash
sudo systemctl restart keyd
```

#### 3. XKB Custom Layout

Crie `~/.config/xkb/symbols/abnt2-custom`:

```xkb
default partial alphanumeric_keys
xkb_symbols "basic" {
    include "br(abnt2)"
    name[Group1] = "Portuguese (Brazil, ABNT2, custom RCtrl)";
    
    // <LSGT> (102nd) = / ? °
    key <LSGT> {
        type= "FOUR_LEVEL",
        symbols[Group1]= [ slash, question, degree, questiondown ]
    };
};
```

#### 4. Hyprland Config

Em `~/.config/hypr/hyprland.conf`:

```conf
input {
    kb_file = /home/USUARIO/.config/xkb/symbols/abnt2-custom
    # Remover kb_layout, kb_variant, kb_model, kb_rules
}
```

#### 5. Recarregar

```bash
hyprctl reload
```

#### Verificar

Use `wev` para testar:

```bash
wev
# Pressione Ctrl Direito → deve mostrar XKB_KEY_slash
```

**Documentação completa**: [lessons.md](~/.claude-mprj/tasks/lessons.md) linhas 29-36

---

## 8. Troubleshooting

### Erro: "Git não encontrado"

```bash
# Linux
sudo pacman -S git      # Arch
sudo apt install git    # Debian/Ubuntu

# macOS
brew install git

# Windows
# Baixe de https://git-scm.com
```

### Erro: "Node.js v16 encontrado — requer v18+"

```bash
# Via nvm (recomendado)
nvm install 20
nvm use 20

# Via package manager
brew install node@20    # macOS
sudo pacman -S nodejs   # Arch
```

### Erro: "Claude Code não encontrado"

```bash
npm install -g @anthropic-ai/claude-code
```

### Erro: "Python 3.12.10 não encontrado"

```bash
# UV instala automaticamente
uv python install 3.12.10
```

### Funções shell não encontradas

Certifique-se de recarregar o shell após instalação:

```bash
# Bash/Zsh
source ~/.bashrc

# Fish
source ~/.config/fish/config.fish

# PowerShell
. $PROFILE
```

### MCPs não aparecem

```bash
# Verificar se foram instalados
claude mcp list

# Reinstalar MCPs
uv run python install.py --mcps-only
```

### Backup de secrets não funciona

O instalador cria backups automaticamente em `~/.claude-md-backups/`. Para restaurar:

```bash
# Listar backups
ls -lt ~/.claude-md-backups/

# Restaurar específico
cp -a ~/.claude-md-backups/20260520-141500/.secrets/* ~/.secrets/
cp -a ~/.claude-md-backups/20260520-141500/.claude-mprj/* ~/.claude-mprj/
```

### Testes falhando após instalação

```bash
cd ~/workspace/claude-md
uv sync --dev
uv run pytest -v
```

---

## Referências

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Infisical Documentation](https://infisical.com/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [README.md](README.md) — Visão geral do projeto
- [UNINSTALL.md](UNINSTALL.md) — Desinstalação completa

---

**Instalador v2.0.0** — Python unificado para Linux, macOS e Windows
