# Instalação e Configuração do Claude Code

Este guia cobre instalação da configuração global e setup de múltiplas contas (MPRJ/Foundry + pessoal PRO).

**Ambientes:**

- **Windows 11**: `D:\workspace\claude-md`
- **Linux Arch (Garuda)**: `$HOME/workspace/claude-md`

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Instalação da Configuração Global](#2-instalação-da-configuração-global)
3. [Token GitLab](#3-token-gitlab)
4. [Variáveis de Ambiente para MCP GitLab](#4-variáveis-de-ambiente-para-mcp-gitlab)
5. [.env — Infisical (por projeto)](#5-env--infisical-por-projeto)
6. [MCP Servers](#6-mcp-servers)
7. [Múltiplas Contas (MPRJ + Pessoal)](#7-múltiplas-contas-mprj--pessoal)
8. [Atualização](#8-atualização)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Pré-requisitos

| Dependência       | Versão mínima | Como instalar                              |
|-------------------|---------------|--------------------------------------------|
| Node.js           | 18+           | https://nodejs.org ou `nvm install --lts`  |
| npm               | incluído      | vem com o Node.js                          |
| Claude Code (CLI) | latest        | `npm install -g @anthropic-ai/claude-code` |

### Verificar instalação

```bash
node --version    # v18.x.x ou superior
claude --version
```

---

## 2. Instalação da Configuração Global

### Linux (Garuda / Arch) — via symlinks (recomendado)

Symlinks fazem `git pull` no repositório refletir imediatamente em `~/.claude/` — sem re-executar o script de instalação.

```bash
cd $HOME/workspace/claude-md

# 1. Criar estrutura de diretórios
mkdir -p ~/.claude/tasks/archive

# 2. Criar symlinks dos arquivos principais
ln -sf "$PWD/CLAUDE.md"    ~/.claude/CLAUDE.md
ln -sf "$PWD/settings.json" ~/.claude/settings.json
ln -sf "$PWD/skills"        ~/.claude/skills
ln -sf "$PWD/commands"      ~/.claude/commands

# 3. Copiar templates de tasks (apenas se não existirem)
[ ! -f ~/.claude/tasks/todo.md ]      && cp tasks/todo.md      ~/.claude/tasks/todo.md
[ ! -f ~/.claude/tasks/lessons.md ]   && cp tasks/lessons.md   ~/.claude/tasks/lessons.md
[ ! -f ~/.claude/tasks/decisions.md ] && cp tasks/decisions.md ~/.claude/tasks/decisions.md

# 4. Criar arquivo de auditoria
touch ~/.claude/audit.log

# 5. Verificar
ls -la ~/.claude/
```

> **Nota sobre symlinks em múltiplas contas:** ao usar `~/.claude-mprj` e `~/.claude-pessoal`, repita `ln -sf` apontando para os mesmos arquivos do repo. As tasks ficam independentes por conta.

---

### Linux — via cópia (alternativa)

Use se symlinks não forem adequados (ex: permissões restritas, containers).

```bash
cd $HOME/workspace/claude-md

mkdir -p ~/.claude/skills ~/.claude/commands ~/.claude/tasks/archive

cp CLAUDE.md ~/.claude/CLAUDE.md
cp settings.json ~/.claude/settings.json
cp -r skills/*   ~/.claude/skills/
cp -r commands/* ~/.claude/commands/

[ ! -f ~/.claude/tasks/todo.md ]      && cp tasks/todo.md      ~/.claude/tasks/todo.md
[ ! -f ~/.claude/tasks/lessons.md ]   && cp tasks/lessons.md   ~/.claude/tasks/lessons.md
[ ! -f ~/.claude/tasks/decisions.md ] && cp tasks/decisions.md ~/.claude/tasks/decisions.md

touch ~/.claude/audit.log
ls ~/.claude/
```

---

### Windows 11 (PowerShell)

```powershell
cd D:\workspace\claude-md

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
if (-not (Test-Path "$env:USERPROFILE\.claude\tasks\lessons.md")) {
    Copy-Item tasks\lessons.md "$env:USERPROFILE\.claude\tasks\lessons.md"
}
if (-not (Test-Path "$env:USERPROFILE\.claude\tasks\decisions.md")) {
    Copy-Item tasks\decisions.md "$env:USERPROFILE\.claude\tasks\decisions.md"
}

# 7. Criar arquivo de auditoria
New-Item -ItemType File -Force -Path "$env:USERPROFILE\.claude\audit.log"

# 8. Verificar
Get-ChildItem "$env:USERPROFILE\.claude\"
```

---

## 3. Token GitLab

Acesse: `https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens`

### Configurações do token

| Campo      | Valor recomendado             |
|------------|-------------------------------|
| Token name | `claude-code-mprj`            |
| Expiration | 1 ano (renovar no vencimento) |
| Scopes     | ver tabela abaixo             |

### Scopes — o máximo que boas práticas permitem

| Scope              | Marcar | Motivo                                                                          |
|--------------------|--------|---------------------------------------------------------------------------------|
| `api`              | ✅      | Acesso completo à API REST — projetos, MRs, issues, pipelines, registry, perfil |
| `read_repository`  | ✅      | Clonar repositórios privados via HTTPS (`api` não cobre git over HTTPS)         |
| `write_repository` | ✅      | Push via HTTPS — necessário para o Claude Code fazer push                       |
| `read_registry`    | ✅      | Pull de imagens do Container Registry                                           |
| `write_registry`   | ✅      | Push de imagens ao Container Registry                                           |
| `read_user`        | ❌      | Redundante — já coberto pelo `api`                                              |
| `create_runner`    | ❌      | Desnecessário — não registramos runners via Claude                              |
| `manage_runner`    | ❌      | Desnecessário                                                                   |
| `ai_features`      | ❌      | Recursos GitLab AI — não utilizado                                              |
| `k8s_proxy`        | ❌      | Proxy Kubernetes — não utilizado                                                |
| `sudo`             | ❌      | Impersonar outros usuários — nunca conceder                                     |

> **Nota:** o scope `api` já inclui acesso de leitura e escrita à maioria dos recursos.
> Os scopes `read_repository` e `write_repository` são necessários separadamente para
> operações git via HTTPS (clone/push), que o `api` não cobre.

### Após criar

```bash
# Copiar o token gerado (exibido apenas uma vez) e definir nas variáveis de ambiente
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
```

> Guardar o token em local seguro — o GitLab não exibe novamente após fechar a página.
> Se perder, revogar e criar um novo.

---

## 4. Variáveis de Ambiente para MCP GitLab

### Linux — Bash (`~/.bashrc` ou `~/.zshrc`)

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_URL="https://gitlab-dti.mprj.mp.br"
```

### Linux — Fish (`~/.config/fish/conf.d/claude.fish`)

```fish
set -x GITLAB_TOKEN "glpat-xxxxxxxxxxxxxxxxxxxx"
set -x GITLAB_URL   "https://gitlab-dti.mprj.mp.br"
```

### Windows — PowerShell Profile

O Profile do PowerShell é executado automaticamente em toda sessão, equivalente ao `.bashrc`.

```powershell
# 1. Verificar se o Profile já existe
Test-Path $PROFILE

# 2. Criar o Profile caso não exista
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Force -Path $PROFILE
}

# 3. Abrir o Profile no editor
notepad $PROFILE
# ou no VS Code:
code $PROFILE
```

Adicionar ao arquivo aberto:

```powershell
# GitLab MPRJ
$env:GITLAB_TOKEN = "glpat-xxxxxxxxxxxxxxxxxxxx"
$env:GITLAB_URL   = "https://gitlab-dti.mprj.mp.br"
```

```powershell
# 4. Recarregar o Profile na sessão atual
. $PROFILE
```

> Se o PowerShell bloquear a execução de scripts, habilitar uma vez:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## 5. .env — Infisical (por projeto)

Cada projeto precisa de um `.env` na raiz com as credenciais de conexão ao Infisical.
**Nunca commitar este arquivo** — adicionar ao `.gitignore`.

```dotenv
# Infisical — credenciais de conexão (não são secrets da aplicação)
INFISICAL_PROJECT_ID=
INFISICAL_TOKEN=
INFISICAL_SITE_URL=https://ncd-infisical.mprj.mp.br/
INFISICAL_PORT=80

# dev | staging | prod
INFISICAL_ENVIRONMENT_SLUG=dev
```

O `secretsloader` lê este `.env`, conecta ao Infisical e injeta todos os secrets do
projeto no `os.environ`. Chamar no topo do `settings/base.py`:

```python
from secretsloader import load_secrets

load_secrets()
```

### .gitignore obrigatório em todo projeto

```gitignore
.env
.env.*
*.env
```

---

## 6. MCP Servers

Os MCPs abaixo correspondem à stack definida em `CLAUDE.md`. Instale os de escopo `global` uma vez por máquina; os `local` e `project` por projeto.

| Server       | Escopo    | Uso                                         |
|--------------|-----------|---------------------------------------------|
| `gitlab`     | `local`   | MRs, issues, pipelines no MPRJ GitLab       |
| `filesystem` | `global`  | Acesso estruturado a arquivos               |
| `memory`     | `global`  | Persistência de contexto cross-session      |
| `postgres`   | `local`   | Queries diretas no banco de dev             |
| `playwright` | `project` | Testes E2E (adicionar em cada projeto)      |

```bash
# GitLab MPRJ (escopo local — credenciais por projeto, não commitado)
claude mcp add --scope local gitlab -- npx -y @modelcontextprotocol/server-gitlab

# Filesystem (escopo global — disponível em toda sessão)
claude mcp add --scope global filesystem -- npx -y @modelcontextprotocol/server-filesystem \
  "$HOME"

# Memory (escopo global — contexto persiste entre sessões)
claude mcp add --scope global memory -- npx -y @modelcontextprotocol/server-memory

# PostgreSQL local (escopo local — por projeto)
claude mcp add --scope local postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:pass@localhost:5432/dev_db"

# Playwright (escopo de projeto — executar na raiz do projeto)
claude mcp add --scope project playwright -- npx @playwright/mcp@latest
```

### Verificar MCPs instalados

```bash
claude mcp list
```

---

## 7. Múltiplas Contas (MPRJ + Pessoal)

Permite usar conta corporativa (Microsoft Foundry / MPRJ) e conta pessoal PRO na mesma máquina,
sem logout manual. Cada conta tem configuração, credenciais e sessão totalmente isoladas.

### Como funciona

O Claude Code usa `~/.claude` (Linux) ou `%USERPROFILE%\.claude` (Windows) para armazenar tudo.
A variável `CLAUDE_CONFIG_DIR` permite apontar para diretórios diferentes por conta.

- **Conta MPRJ (Microsoft Foundry)**: autentica via API Key — sem `/login`, sem browser
- **Conta pessoal PRO**: autentica via OAuth normal com `/login`

---

### 7.1. Linux (Garuda / Arch)

#### Passo 1: Criar os diretórios de configuração

```bash
mkdir -p ~/.claude-mprj ~/.claude-pessoal
```

Opcional — preservar config atual na conta pessoal:

```bash
cp -R ~/.claude ~/.claude-pessoal
```

#### Passo 2: Criar arquivo de segredos para a API Key

```bash
mkdir -p ~/.secrets
# Armazenar apenas o valor da key (sem sintaxe shell)
echo 'sk-ant-...' > ~/.secrets/claude-mprj.key
chmod 600 ~/.secrets/claude-mprj.key
```

#### Passo 3: Configurar o shell

**Bash / Zsh — `~/.bashrc` ou `~/.zshrc`:**

```bash
# --- Claude Code: múltiplas contas ---

# Conta corporativa (MPRJ / Microsoft Foundry)
# Autenticação via API Key — não usa /login, não abre browser
function claude-mprj() {
    CLAUDE_CONFIG_DIR=~/.claude-mprj \
    CLAUDE_CODE_USE_FOUNDRY=1 \
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
    ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key)" \
    command claude "$@"
}

# Conta pessoal PRO — autenticação OAuth normal
function claude-pro() {
    CLAUDE_CONFIG_DIR=~/.claude-pessoal \
    command claude "$@"
}

# Bloqueia o comando genérico para evitar uso na conta errada
alias claude="echo 'Use: claude-mprj  ou  claude-pro'"
```

> **Por que `command claude`?**
> Bypassa aliases no Bash/Zsh, chamando o binário diretamente. Sem isso, o alias bloqueador interceptaria a chamada.

**Fish — `~/.config/fish/conf.d/claude.fish`:**

```fish
# Conta corporativa (MPRJ / Microsoft Foundry)
function claude-mprj
    env CLAUDE_CONFIG_DIR=~/.claude-mprj \
        CLAUDE_CODE_USE_FOUNDRY=1 \
        ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
        ANTHROPIC_FOUNDRY_API_KEY=(cat ~/.secrets/claude-mprj.key) \
        command claude $argv
end

# Conta pessoal PRO
function claude-pro
    env CLAUDE_CONFIG_DIR=~/.claude-pessoal \
        command claude $argv
end

# Bloqueia o comando genérico
function claude
    echo 'Use: claude-mprj  ou  claude-pro'
end
```

Recarregar (Bash/Zsh):

```bash
source ~/.bashrc   # ou source ~/.zshrc
```

#### Passo 4: Autenticar cada conta (uma única vez)

```bash
# Conta MPRJ — já autentica via API Key ao abrir
claude-mprj

# Conta pessoal — autenticação OAuth
claude-pro
# Dentro da sessão, rode: /login
# O browser abrirá — entre com as credenciais pessoais PRO
```

#### Passo 5: Uso diário

```bash
claude-mprj    # conta MPRJ / Foundry
claude-pro     # conta pessoal PRO
```

#### Verificar se as funções estão carregadas

```bash
type claude-mprj
# Saída esperada: claude-mprj is a function
```

---

### 7.2. Windows 11

#### Passo 1: Criar os diretórios de configuração

Abra o **PowerShell**:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude-mprj"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude-pessoal"
```

Opcional — copiar config atual:

```powershell
Copy-Item -Recurse "$env:USERPROFILE\.claude\*" "$env:USERPROFILE\.claude-pessoal\"
```

#### Passo 2: Descobrir o caminho real do `claude.exe`

Este passo é obrigatório — o caminho varia por instalação.

```powershell
Get-Command claude -CommandType Application | Select-Object -ExpandProperty Source
```

Exemplo de saída:

```
C:\Users\welington.souza\.local\bin\claude.exe
```

Guarde esse caminho — será usado nas funções.

#### Passo 3: Registrar a API Key Foundry (feito uma única vez)

```powershell
[Environment]::SetEnvironmentVariable(
    "ANTHROPIC_FOUNDRY_API_KEY",
    "sk-ant-...",
    "User"
)
```

> Persiste entre sessões sem expor a key em texto puro no `$PROFILE`.
> Abra um novo terminal após rodar para a variável ficar disponível.

#### Passo 4: Criar funções no perfil do PowerShell

Abra o arquivo de perfil:

```powershell
notepad $PROFILE
```

> Se o arquivo não existir, o Notepad perguntará se deseja criar — confirme com Sim.

Adicione ao final, **substituindo o caminho pelo resultado do Passo 2**:

```powershell
# --- Claude Code: múltiplas contas ---

# Caminho real do executável (descubra com: Get-Command claude -CommandType Application)
$claudeExe = "C:\Users\welington.souza\.local\bin\claude.exe"

function claude-mprj {
    # Autenticação via API Key (Microsoft Foundry) — sem /login, sem browser
    # ANTHROPIC_FOUNDRY_API_KEY vem das variáveis de ambiente do usuário (Passo 3)
    $env:CLAUDE_CONFIG_DIR          = "$env:USERPROFILE\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY    = "1"
    $env:ANTHROPIC_FOUNDRY_RESOURCE = "gomas-mok8hc25-eastus2"
    & $claudeExe @args
    Remove-Item Env:\CLAUDE_CONFIG_DIR          -ErrorAction SilentlyContinue
    Remove-Item Env:\CLAUDE_CODE_USE_FOUNDRY    -ErrorAction SilentlyContinue
    Remove-Item Env:\ANTHROPIC_FOUNDRY_RESOURCE -ErrorAction SilentlyContinue
}

function claude-pro {
    # Autenticação OAuth normal — use /login na primeira vez
    $env:CLAUDE_CONFIG_DIR = "$env:USERPROFILE\.claude-pessoal"
    & $claudeExe @args
    Remove-Item Env:\CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
}

function claude {
    Write-Host "Use: claude-mprj  ou  claude-pro" -ForegroundColor Yellow
}
```

> **Por que `& $claudeExe`?**
> O `&` (call operator) chama o binário diretamente pelo caminho completo,
> ignorando a função bloqueadora `claude`.

Salve e recarregue:

```powershell
. $PROFILE
```

> **Erro de ExecutionPolicy?** Rode antes:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> . $PROFILE
> ```

#### Passo 5: Autenticar cada conta (uma única vez)

```powershell
# Conta MPRJ — já autentica via API Key ao abrir
claude-mprj

# Conta pessoal — autenticação OAuth
claude-pro
# Dentro da sessão: /login  → browser abre, entre com credenciais PRO
```

#### Passo 6: Verificar se as funções estão carregadas

```powershell
Get-Command claude-mprj
# Esperado: CommandType = Function
```

#### Passo 7: Uso diário

```powershell
claude-mprj    # conta MPRJ / Foundry
claude-pro     # conta pessoal PRO
```

---

### 7.3. Alternativa Windows — CMD (Prompt de Comando)

Se preferir usar CMD, descubra o caminho do executável primeiro:

```cmd
where claude
```

Crie dois arquivos `.bat` em qualquer pasta do PATH (ex: `C:\Users\welington.souza\bin\`):

**`claude-mprj.bat`**

```bat
@echo off
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude-mprj
set CLAUDE_CODE_USE_FOUNDRY=1
set ANTHROPIC_FOUNDRY_RESOURCE=gomas-mok8hc25-eastus2
rem ANTHROPIC_FOUNDRY_API_KEY deve estar nas variáveis de ambiente do usuário
"C:\Users\welington.souza\.local\bin\claude.exe" %*
set CLAUDE_CONFIG_DIR=
set CLAUDE_CODE_USE_FOUNDRY=
set ANTHROPIC_FOUNDRY_RESOURCE=
```

**`claude-pro.bat`**

```bat
@echo off
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude-pessoal
"C:\Users\welington.souza\.local\bin\claude.exe" %*
set CLAUDE_CONFIG_DIR=
```

---

### 7.4. Comportamento por tipo de configuração

| Configuração                                  | Isolada por conta? | Observação                               |
|-----------------------------------------------|--------------------|------------------------------------------|
| Credenciais / sessão OAuth                    | ✅ Sim              | Cada diretório tem seu próprio login     |
| API Key Foundry (`ANTHROPIC_FOUNDRY_API_KEY`) | ✅ Sim              | Injetada só na função `claude-mprj`      |
| `CLAUDE.md` global (`~/.claude/`)             | ✅ Sim              | Separado por conta                       |
| `CLAUDE.md` de projeto (no repo)              | ❌ Não              | Fica no repo, compartilhado entre contas |
| MCP servers                                   | ✅ Sim              | Configurar separadamente em cada conta   |
| Histórico de sessões                          | ✅ Sim              | Totalmente isolado                       |

---

### 7.5. Configuração por projeto (opcional)

Para fixar uma conta específica por repositório, use `direnv` ou adicione ao `.envrc` na raiz do projeto:

```bash
# Linux — .envrc (requer direnv instalado)
export CLAUDE_CONFIG_DIR="$HOME/.claude-mprj"
```

```powershell
# Windows — adicionar ao $PROFILE com lógica condicional por diretório
# ou configurar via variável de ambiente do usuário
```

---

### 7.6. Verificando a conta ativa

Dentro de qualquer sessão do Claude Code:

```
/status
```

Ou no terminal:

```bash
# Linux / Fish
echo $CLAUDE_CONFIG_DIR

# Windows PowerShell
echo $env:CLAUDE_CONFIG_DIR
```

---

### 7.7. Estrutura final de diretórios

```
~/ (Linux) ou %USERPROFILE%\ (Windows)
├── .claude/              # diretório original (pode ser descartado)
├── .claude-mprj/         # conta corporativa MPRJ / Microsoft Foundry
│   ├── credentials       # sessão Foundry
│   ├── settings.json
│   └── ...
└── .claude-pessoal/      # conta pessoal PRO
    ├── credentials       # token OAuth pessoal
    ├── settings.json
    └── ...

~/.secrets/               # Linux apenas
└── claude-mprj.key       # API Key em texto puro (chmod 600, fora do controle de versão)
```

---

## 8. Atualização

### Linux — com symlinks (nenhuma ação necessária)

Se a instalação usou symlinks (seção 2), basta atualizar o repositório:

```bash
cd $HOME/workspace/claude-md
git pull
```

Os arquivos em `~/.claude/` já apontam para o repositório — nenhuma cópia adicional necessária.

---

### Linux — com cópia

```bash
cd $HOME/workspace/claude-md
git pull

# Atualizar todos os diretórios de contas existentes
for dir in ~/.claude ~/.claude-mprj ~/.claude-pessoal; do
    [ -d "$dir" ] || continue
    cp CLAUDE.md "$dir/CLAUDE.md"
    cp settings.json "$dir/settings.json"
    cp -r skills/*   "$dir/skills/"
    cp -r commands/* "$dir/commands/"
    echo "Atualizado: $dir"
done
```

---

### Windows

```powershell
cd D:\workspace\claude-md
git pull

foreach ($suffix in @("", "-mprj", "-pessoal")) {
    $dir = "$env:USERPROFILE\.claude$suffix"
    if (Test-Path $dir) {
        Copy-Item CLAUDE.md "$dir\CLAUDE.md"
        Copy-Item settings.json "$dir\settings.json"
        Copy-Item -Recurse -Force skills\*   "$dir\skills\"
        Copy-Item -Recurse -Force commands\* "$dir\commands\"
        Write-Host "Atualizado: $dir"
    }
}
```

---

## 9. Troubleshooting

### `claude: command not found`

```bash
# Verificar se o npm global está no PATH
npm bin -g        # exibe o diretório — deve estar no PATH
echo $PATH
```

Adicionar ao shell se necessário:

```bash
# Bash / Zsh
export PATH="$(npm bin -g):$PATH"

# Fish
fish_add_path (npm bin -g)
```

---

### MCP server não aparece em `/mcp`

```bash
# Verificar MCPs registrados
claude mcp list

# Remover e re-adicionar com log de erro
claude mcp remove gitlab
claude mcp add --scope local gitlab -- npx -y @modelcontextprotocol/server-gitlab
```

---

### `claude-mprj` abre browser em vez de autenticar via API Key

Verificar se `ANTHROPIC_FOUNDRY_API_KEY` está sendo injetada:

```bash
# Bash/Zsh — testar direto
ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key)" \
CLAUDE_CODE_USE_FOUNDRY=1 \
claude --version

# Fish — testar direto
env ANTHROPIC_FOUNDRY_API_KEY=(cat ~/.secrets/claude-mprj.key) \
    CLAUDE_CODE_USE_FOUNDRY=1 \
    claude --version
```

---

### PowerShell: `could not be loaded because running scripts is disabled`

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
. $PROFILE
```

---

### Symlink quebrado após mover o repositório

```bash
# Recriar os symlinks com o novo caminho
cd $HOME/novo-caminho/claude-md
ln -sf "$PWD/CLAUDE.md"     ~/.claude/CLAUDE.md
ln -sf "$PWD/settings.json" ~/.claude/settings.json
ln -sf "$PWD/skills"        ~/.claude/skills
ln -sf "$PWD/commands"      ~/.claude/commands
```
