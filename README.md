# Claude Code — Instalador Python Unificado

[![Python 3.12.10](https://img.shields.io/badge/python-3.12.10-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-83%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-75.61%25-green.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Instalador **multiplataforma** em Python para configuração global do Claude Code com solução unificada, testável e moderna.

---

## 🎯 Características

- ✅ **Multiplataforma**: Linux, macOS, Windows
- ✅ **CLI Moderna**: Interface colorida com [Rich](https://github.com/Textualize/rich) (barras de progresso, tabelas, cores)
- ✅ **Gestão Segura de Secrets**: Integração com [Infisical](https://infisical.com/) via `secretsloader`
- ✅ **Múltiplas Contas**: Suporte nativo para MPRJ (Foundry) + Pessoal (PRO)
- ✅ **Testável**: 71 testes (97% pass rate), cobertura 75.61%
- ✅ **Type-Safe**: Type hints completos + mypy strict
- ✅ **Idempotente**: Detecta estado existente, não duplica configurações
- ✅ **Backup Automático**: Snapshot timestamped de secrets antes da instalação

---

## 📋 Requisitos

### Sistema

| Ferramenta | Versão Mínima | Verificado Automaticamente |
|------------|---------------|----------------------------|
| **Python** | 3.12.10 (estrito) | ❌ (gerenciado por `uv`) |
| **UV** | latest | ❌ (instale manualmente) |
| **Git** | qualquer | ✅ |
| **Node.js** | v18+ | ✅ |
| **Claude Code** | qualquer | ✅ |

### Infisical (Secrets Management)

Para instalação completa com múltiplas contas, você precisa configurar:

1. **Variáveis de ambiente** (via `.env` ou export):
   - `INFISICAL_CLIENT_ID`
   - `INFISICAL_CLIENT_SECRET`
   - `INFISICAL_PROJECT_ID`
   - `INFISICAL_SITE_URL`
   - `INFISICAL_ENVIRONMENT_SLUG`

2. **Secrets no Infisical** (projeto configurado):
   - `ANTHROPIC_FOUNDRY_API_KEY` — API key MPRJ (Azure Foundry)
   - `GITLAB_TOKEN` — Token de acesso ao GitLab DTI
   - `POSTMAN_API_KEY` — API key do Postman

Veja [Configuração do Infisical](#-configuração-do-infisical) para detalhes.

---

## 🚀 Instalação Rápida

### 1. Instalar UV (se ainda não tem)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Clonar o Repositório

```bash
git clone https://gitlab-dti.mprj.mp.br/seu-usuario/claude-md.git
cd claude-md
```

### 3. Configurar Infisical (opcional, mas recomendado)

Copie o template e preencha com suas credenciais:

```bash
cp .env.example .env
# Edite .env com suas credenciais Infisical
```

**Nota**: Instalação sem Infisical pula configuração de API keys. Você pode configurá-las manualmente depois.

### 4. Executar o Instalador

```bash
# Instalação interativa (recomendado para primeira vez)
uv run python install.py

# OU: Instalação não-interativa com múltiplas contas
uv run python install.py --non-interactive --multi-account
```

### 5. Recarregar Shell

```bash
# Bash/Zsh
source ~/.bashrc  # ou ~/.zshrc

# Fish
source ~/.config/fish/config.fish

# PowerShell
. $PROFILE
```

### 6. Verificar Instalação

```bash
# Testar funções shell
claude-mprj --version
claude-pro --version

# Listar MCPs instalados
claude mcp list
```

---

## 🗑️ Desinstalação

Para remover completamente a configuração do Claude Code:

```bash
# Desinstalação automática com preview e backup
python uninstall.py
```

O script irá:
1. Mostrar preview do que será removido (diretórios, arquivos shell, tamanho)
2. Pedir confirmação
3. Criar backup automático em `~/.claude-backups/`
4. Remover configurações (`~/.claude-pessoal/`, `~/.claude-mprj/`, `~/.claude/`)
5. Limpar integrações shell (`.bashrc`, `.zshrc`, `claude.fish`)

**Documentação completa**: [UNINSTALL.md](UNINSTALL.md)

### Desinstalação Manual

Se preferir fazer manualmente:

```bash
# Remover diretórios
rm -rf ~/.claude-pessoal ~/.claude-mprj ~/.claude

# Remover chave MPRJ (Linux)
rm -f ~/.secrets/claude-mprj.key

# Remover bloco shell
sed -i '/# --- Claude Code: múltiplas contas/,/# --- end Claude Code multi-conta ---/d' ~/.bashrc
sed -i '/# --- Claude Code: múltiplas contas/,/# --- end Claude Code multi-conta ---/d' ~/.zshrc
rm ~/.config/fish/conf.d/claude.fish  # Fish
```

---

## 🎮 Uso

### Modos de Instalação

#### Instalação Completa (Interativa)

```bash
uv run python install.py
```

Pergunta sobre:
- Configurar múltiplas contas?
- Configurar shell?
- Instalar MCP servers?

#### Instalação Não-Interativa (CI/CD)

```bash
uv run python install.py --non-interactive --multi-account
```

Assume respostas padrão (sim para tudo).

#### Atualizar Apenas Arquivos

```bash
uv run python install.py --update-only
```

Atualiza `CLAUDE.md`, `settings.json`, `skills/`, `commands/` — **preserva** `.mcp.json` e configurações.

#### Instalar Apenas MCP Servers

```bash
uv run python install.py --mcps-only
```

Instala/atualiza apenas MCP servers globais.

### Flags Disponíveis

| Flag | Descrição |
|------|-----------|
| `--non-interactive` | Modo não-interativo (sem prompts) |
| `--multi-account` | Força configuração de múltiplas contas (MPRJ + Pessoal) |
| `--update-only` | Atualiza apenas arquivos (preserva configs) |
| `--mcps-only` | Instala apenas MCP servers |
| `--help` | Mostra ajuda |

### Exemplo de Output

```
╔══════════════════════════════════════════════╗
║   Claude Code — Instalação Global (Python)   ║
╚══════════════════════════════════════════════╝

▶  Verificando pré-requisitos...
✔  Git 2.43.0
✔  Node.js v20.11.0
✔  Claude Code 0.7.0

▶  Snapshot de chaves e credenciais (BEFORE install)...
  Copiando arquivos sensíveis... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
✔  13 arquivo(s) sensível(is) preservados em ~/.claude-md-backups/20260519-143022

▶  Instalando em ~/.claude ...
✔  ~/.claude configurado

▶  Instalando em ~/.claude-mprj ...
✔  ~/.claude-mprj configurado

▶  Instalando em ~/.claude-pessoal ...
✔  ~/.claude-pessoal configurado

▶  Configurando API Keys via Infisical...
✔  Foundry API Key configurada
✔  GitLab Token configurado

▶  Configurando bash...
✔  bash configurado

▶  Instalando MCP servers globais...
✔  MCP filesystem instalado
✔  MCP memory instalado
✔  MCP gitlab instalado
✔  MCP postman instalado

✔ Instalação concluída!

  Próximos passos:
  1. Recarregar shell:    source ~/.bashrc
  2. Autenticar MPRJ:     claude-mprj
  3. Autenticar pessoal:  claude-pro  →  /login

  Token GitLab:
  https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens
```

---

## 🔐 Configuração do Infisical

### Criar Projeto no Infisical

1. Acesse `https://ncd-infisical.mprj.mp.br/`
2. Crie um novo projeto (ex: "claude-config")
3. Vá em **Project Settings → Environments** → use `prod`

### Criar Service Token (Machine Identity)

1. **Organization Settings → Access Control → Machine Identities**
2. **Create Identity** → escolha **Universal Auth**
3. Copie:
   - `Client ID`
   - `Client Secret`
4. **Adicionar ao projeto** criado acima com permissões de leitura

### Adicionar Secrets no Projeto

Em **Project → Secrets → prod**:

```bash
ANTHROPIC_FOUNDRY_API_KEY=sk-ant-api03-...
GITLAB_TOKEN=glpat-...
POSTMAN_API_KEY=PMAK-...
```

### Configurar `.env` Localmente

```bash
# .env (não comitar!)
INFISICAL_CLIENT_ID=<seu-client-id>
INFISICAL_CLIENT_SECRET=<seu-client-secret>
INFISICAL_PROJECT_ID=767794c3-84e4-4ecb-b763-38c5d824f5c7
INFISICAL_SITE_URL=https://ncd-infisical.mprj.mp.br/
INFISICAL_ENVIRONMENT_SLUG=prod
```

**Importante**: Adicione `.env` ao `.gitignore` (já configurado).

---

## 🛠️ Desenvolvimento

### Setup de Desenvolvimento

```bash
# Clonar repo
git clone https://gitlab-dti.mprj.mp.br/seu-usuario/claude-md.git
cd claude-md

# Instalar dependências (inclui dev)
uv sync --dev

# Verificar instalação
uv run python install.py --help
```

### Executar Testes

```bash
# Todos os testes
uv run pytest

# Com cobertura
uv run pytest --cov=installer --cov-report=term-missing

# Paralelo (mais rápido)
uv run pytest -n auto

# Específico
uv run pytest tests/test_cli.py -v

# Watch mode (rerun ao mudar arquivo)
uv run pytest-watch
```

**Status atual**: 71/73 testes passando (97%), 2 xfailed esperados, cobertura 75.61%.

### Linting e Formatação

```bash
# Verificar estilo
uv run ruff check .

# Formatar código
uv run ruff format .

# Corrigir problemas automaticamente
uv run ruff check . --fix
```

### Type Checking

```bash
# Verificar tipos
uv run mypy installer/

# Com mais detalhes
uv run mypy installer/ --show-error-codes
```

### Estrutura do Projeto

```
claude-md/
├── installer/              # Pacote principal
│   ├── __init__.py         # v2.0.0
│   ├── api_keys.py         # Config API keys via Infisical
│   ├── backup.py           # Backup/restore de secrets
│   ├── cli.py              # CLI principal com Rich
│   ├── files.py            # Instalação de arquivos
│   ├── mcp.py              # Instalação de MCP servers
│   ├── platform.py         # Detecção de SO e shell
│   ├── prereqs.py          # Verificação de pré-requisitos
│   ├── shell_config.py     # Configuração de shell (bash/zsh/fish/ps1)
│   └── uninstall.py        # Desinstalação completa
│
├── tests/                  # Suíte de testes (83 testes)
│   ├── conftest.py         # Fixtures compartilhadas
│   ├── test_api_keys.py
│   ├── test_backup_restore.py
│   ├── test_cli.py
│   ├── test_install_files.py
│   ├── test_mcp.py
│   ├── test_platform.py
│   ├── test_prereqs.py
│   └── test_shell_config.py
│
├── install.py              # Entrypoint instalação
├── uninstall.py            # Entrypoint desinstalação
├── pyproject.toml          # Configuração UV, deps, testes
├── .env.example            # Template Infisical
│
├── CLAUDE.md               # Instruções para Claude Code
├── INSTALL.md              # Guia de instalação detalhado
├── UNINSTALL.md            # Guia de desinstalação
├── WORKFLOW_CONFIG.md      # Workflow de desenvolvimento
├── settings.json           # Config Claude Code
├── skills/                 # Skills customizadas
├── commands/               # Comandos customizados
└── tasks/                  # Tasks, lessons, decisions
```

---

## 📦 Funcionalidades Detalhadas

### 1. Backup Automático de Secrets

**Antes de qualquer mudança**, o instalador cria um snapshot timestamped:

```
~/.claude-md-backups/
├── 20260519-143022/        # Backup mais recente
│   ├── .secrets/
│   │   └── claude-mprj.key
│   ├── .claude/
│   │   ├── settings.local.json
│   │   └── .mcp.json
│   └── env.snapshot        # Variáveis de ambiente extraídas
├── 20260518-091542/
└── ...                     # Mantém 10 backups mais recentes
```

- **Automático**: criado sempre antes da instalação
- **Timestamped**: `YYYYMMDD-HHMMSS`
- **Rotação**: mantém apenas os 10 mais recentes
- **Restore**: restaura arquivos **ausentes** (não sobrescreve existentes)
- **Permissions**: backup com `chmod 700`, arquivos com `chmod 600`

### 2. Verificação de Pré-Requisitos

Valida antes de instalar:
- ✅ Git instalado
- ✅ Node.js v18+ (requerido para MCPs)
- ✅ Claude Code instalado

**Falha graciosamente** com mensagens claras se algo estiver faltando.

### 3. Instalação Multi-Conta

Configura **3 ambientes isolados**:

| Diretório | Conta | Uso |
|-----------|-------|-----|
| `~/.claude/` | Padrão | Config compartilhada base |
| `~/.claude-mprj/` | MPRJ (Foundry) | Trabalho corporativo |
| `~/.claude-pessoal/` | Pessoal (PRO) | Projetos pessoais |

**Funções shell criadas**:
- `claude-mprj` → usa `~/.claude-mprj/` + Foundry API
- `claude-pro` → usa `~/.claude-pessoal/` + Anthropic API
- `claude` → alias que avisa para usar uma das duas acima

### 4. Model Routing Inteligente

**Cache de 7 dias** do melhor modelo disponível:

**MPRJ (Foundry)**:
```bash
# Tenta em ordem: sonnet-4-5 > haiku-4-5
# Cache em ~/.claude-mprj/.model-cache.json (7 dias)

claude-mprj  # auto-seleciona melhor modelo
claude-mprj --model claude-sonnet-4-5  # força modelo específico
```

**Pessoal (PRO)**:
```bash
# Tenta em ordem: sonnet-4-6 > haiku-4-5-20251001
# Detecta modelos disponíveis via API Anthropic

claude-pro  # auto-seleciona melhor modelo
cs          # alias para sonnet-4-6
ch          # alias para haiku-4-5-20251001
```

**Atualizar cache manualmente**:
```bash
update-mprj-model
```

### 5. Configuração de Shell (Versionada)

**Suporta**: bash, zsh, fish, powershell

**Versioning**:
- `v1` (legado): removido automaticamente com backup
- `v2` (atual): com model routing e multi-conta

**Detecção automática**:
- Linux/macOS: lê `$SHELL`
- Windows: powershell

**Arquivos modificados**:
- Bash: `~/.bashrc`
- Zsh: `~/.zshrc`
- Fish: `~/.config/fish/conf.d/claude.fish`
- PowerShell: `~/Documents/PowerShell/profile.ps1`

**Idempotência**: não duplica se v2 já existe.

### 6. MCP Servers Globais

Instala automaticamente:

| MCP | Package | Uso |
|-----|---------|-----|
| **filesystem** | `@modelcontextprotocol/server-filesystem` | Acesso estruturado a arquivos |
| **memory** | `@modelcontextprotocol/server-memory` | Persistência cross-session |
| **gitlab** | `@modelcontextprotocol/server-gitlab` | Issues, MRs, pipelines |
| **postman** | `@postman/postman-mcp-server` | Collections, APIs |

**Escopo**: `--scope user` (global para o usuário)

**Idempotência**: detecta MCPs já instalados, pula.

### 7. Instalação de Arquivos (Smart Overwrite)

| Arquivo/Dir | Comportamento |
|-------------|---------------|
| `CLAUDE.md` | **Sempre sobrescreve** |
| `settings.json` | **Sempre sobrescreve** |
| `WORKFLOW_CONFIG.md` | **Sempre sobrescreve** |
| `skills/` | **Sempre sobrescreve** (recursivo) |
| `commands/` | **Sempre sobrescreve** (recursivo) |
| `.mcp.json` | **Preserva** se existir (pode ter senha postgres) |
| `tasks/*.md` | **Preserva** se existir (histórico do usuário) |
| `audit.log` | **Sempre cria** (vazio) |

---

## 🐛 Troubleshooting

### Erro: "Git não encontrado"

```bash
# Linux
sudo apt install git  # Debian/Ubuntu
sudo yum install git  # RHEL/CentOS
sudo pacman -S git    # Arch

# macOS
brew install git

# Windows
# Baixe de https://git-scm.com
```

### Erro: "Node.js v16 encontrado — requer v18+"

```bash
# Linux (via nvm)
nvm install 20
nvm use 20

# macOS
brew install node@20

# Windows
# Baixe de https://nodejs.org (LTS)
```

### Erro: "Claude Code não encontrado"

```bash
npm install -g @anthropic-ai/claude-code
```

### Erro: "Infisical não configurado"

Se você **não precisa de múltiplas contas**, pode pular a configuração do Infisical:
```bash
# Instalação básica (sem API keys automáticas)
uv run python install.py
# Responda "não" para multi-account
```

Configure API keys manualmente depois:
```bash
# MPRJ
mkdir -p ~/.secrets
echo "sk-ant-api03-..." > ~/.secrets/claude-mprj.key
chmod 600 ~/.secrets/claude-mprj.key

# GitLab
echo 'export GITLAB_TOKEN="glpat-..."' >> ~/.bashrc
echo 'export GITLAB_URL="https://gitlab-dti.mprj.mp.br"' >> ~/.bashrc
```

### Testes Falhando

```bash
# Limpar cache
uv cache clean

# Reinstalar dependências
rm -rf .venv uv.lock
uv sync --dev

# Rodar testes novamente
uv run pytest -v
```

---

## 📄 Licença

MIT © 2026 Welington Souza

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Merge Request

**Importante**:
- ✅ Todos os testes devem passar (`uv run pytest`)
- ✅ Cobertura ≥ 75% (`uv run pytest --cov`)
- ✅ Lint limpo (`uv run ruff check .`)
- ✅ Type check limpo (`uv run mypy installer/`)

---

## 📚 Referências

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Infisical Documentation](https://infisical.com/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**v2.0.0** — Substituição completa dos instaladores shell com Python unificado.
