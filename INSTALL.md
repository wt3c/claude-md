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
9. [Teclado ThinkPad T14 Gen 2i — ABNT2](#9-teclado-thinkpad-t14-gen-2i--abnt2-garuda-linux--hyprland)
10. [Troubleshooting](#10-troubleshooting)

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

### Linux (Garuda / Arch)

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

Os MCPs abaixo correspondem à stack definida em `CLAUDE.md`.

> **Como o Claude Code armazena MCPs:** `claude mcp add` grava em `.claude.json` (arquivo interno,
> nunca commitado). O campo `mcpServers` do `settings.json` **não é lido** pelo CLI — ignore-o para
> este fim. `.claude.json` está no `.gitignore` deste repositório.

| Server       | Escopo    | Credencial            | Uso                                         |
|--------------|-----------|----------------------|---------------------------------------------|
| `filesystem` | `user`    | —                    | Acesso estruturado a arquivos               |
| `memory`     | `user`    | —                    | Persistência de contexto cross-session      |
| `gitlab`     | `user`    | `GITLAB_TOKEN` (env) | MRs, issues, pipelines no MPRJ GitLab       |
| `postgres`   | `user`    | connection string    | Queries diretas no banco de dev             |
| `postman`    | `user`    | `POSTMAN_API_KEY`    | Collections, environments, APIs Postman     |
| `playwright` | `project` | —                    | Testes E2E (adicionar em cada projeto)      |

---

### 6.1. Registrar MCPs — comando padrão

Todos os MCPs são registrados via `claude mcp add`. Use `--scope user` para disponibilizar
em todas as sessões da conta, ou `--scope project` para um projeto específico.

```bash
# Filesystem
claude mcp add --scope user filesystem -- npx -y @modelcontextprotocol/server-filesystem "$HOME"

# Memory
claude mcp add --scope user memory -- npx -y @modelcontextprotocol/server-memory

# GitLab MPRJ (token via variável de ambiente no shell)
claude mcp add --scope user gitlab -- npx -y @modelcontextprotocol/server-gitlab

# Playwright (por projeto — executar na raiz do projeto)
claude mcp add --scope project playwright -- npx @playwright/mcp@latest
```

---

### 6.2. PostgreSQL (connection string com credenciais)

O postgres usa `--scope user` normalmente — as credenciais ficam em `.claude.json`, que já
está no `.gitignore` e nunca é commitado.

```bash
claude mcp add --scope user postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://USER:PASS@HOST:5432/DATABASE"
```

**Múltiplas contas:** registrar separadamente em cada conta usando `CLAUDE_CONFIG_DIR`:

```bash
# Conta pessoal
CLAUDE_CONFIG_DIR=~/.claude-pessoal claude mcp add --scope user postgres -- \
  npx -y @modelcontextprotocol/server-postgres "postgresql://USER:PASS@HOST:5432/DATABASE"

# Conta MPRJ
CLAUDE_CONFIG_DIR=~/.claude-mprj claude mcp add --scope user postgres -- \
  npx -y @modelcontextprotocol/server-postgres "postgresql://USER:PASS@HOST:5432/DATABASE"
```

**Verificar conexão:**
```bash
claude mcp list
# postgres: npx ... - ✓ Connected
```

---

### 6.3. Postman (API key)

```bash
claude mcp add --scope user postman \
  -e POSTMAN_API_KEY=SUA_KEY_AQUI \
  -- npx -y @postman/postman-mcp-server
```

Gere a API Key em: **postman.com → Account Settings → API Keys → Generate API Key**

**Múltiplas contas:**

```bash
# Conta pessoal
CLAUDE_CONFIG_DIR=~/.claude-pessoal claude mcp add --scope user postman \
  -e POSTMAN_API_KEY=SUA_KEY_AQUI -- npx -y @postman/postman-mcp-server

# Conta MPRJ
CLAUDE_CONFIG_DIR=~/.claude-mprj claude mcp add --scope user postman \
  -e POSTMAN_API_KEY=SUA_KEY_AQUI -- npx -y @postman/postman-mcp-server
```

---

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

# --- Claude Code: Model Routing -----------------------------------------------
_CLAUDE_PRO_MODEL=""
_claude_model_priority=("claude-sonnet-4-6" "claude-haiku-4-5-20251001")

_get_anthropic_models() {
    local creds="$HOME/.claude-pessoal/.credentials.json"
    [[ ! -f "$creds" ]] && return 1
    command -v python3 &>/dev/null || return 1
    local token
    token=$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
print(d['claudeAiOauth']['accessToken'])
" "$creds" 2>/dev/null) || return 1
    curl -sf "https://api.anthropic.com/v1/models" \
        -H "Authorization: Bearer $token" \
        -H "anthropic-version: 2023-06-01" | \
        python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]" 2>/dev/null
}

_select_best_model() {
    local available="$1" fallback="$2"
    for m in "${_claude_model_priority[@]}"; do
        echo "$available" | grep -qxF "$m" && { echo "$m"; return; }
    done
    echo "$fallback"
}

_get_mprj_model() {
    local cache="$HOME/.claude-mprj/.model-cache.json"
    if [[ -f "$cache" ]] && command -v python3 &>/dev/null; then
        local ts age
        ts=$(python3 -c "
import json, sys
from datetime import datetime, timezone
with open(sys.argv[1]) as f:
    d = json.load(f)
dt = datetime.fromisoformat(d['cached_at'].replace('Z','+00:00'))
print(int(dt.astimezone(timezone.utc).timestamp()))
" "$cache" 2>/dev/null || echo 0)
        age=$(( $(date +%s) - ts ))
        (( age < 604800 )) && \
            python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" "$cache" 2>/dev/null && return
    fi

    printf '  \033[1;33m[claude-mprj] Detectando modelo disponivel...\033[0m\n' >&2
    local best="claude-haiku-4-5-20251001"
    for m in "${_claude_model_priority[@]}"; do
        CLAUDE_CONFIG_DIR="$HOME/.claude-mprj" \
        CLAUDE_CODE_USE_FOUNDRY=1 \
        ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
        ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \
        command claude --model "$m" -p "." --print --output-format json >/dev/null 2>&1 \
            && best="$m" && break
    done

    command -v python3 &>/dev/null && python3 -c "
import json, sys
from datetime import datetime, timezone
data = {'model': sys.argv[1], 'cached_at': datetime.now(timezone.utc).isoformat()}
with open(sys.argv[2], 'w') as f:
    json.dump(data, f)
" "$best" "$cache" 2>/dev/null
    printf '  \033[0;36m[claude-mprj] modelo: %s (cache 7 dias)\033[0m\n' "$best" >&2
    echo "$best"
}

update-mprj-model() {
    rm -f "$HOME/.claude-mprj/.model-cache.json"
    CLAUDE_CONFIG_DIR="$HOME/.claude-mprj" \
    CLAUDE_CODE_USE_FOUNDRY=1 \
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
    ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \
    _get_mprj_model > /dev/null
}

# --- Claude Code: funções por conta ------------------------------------------
function claude-mprj() {
    local extra_args=() has_model=false
    for arg in "$@"; do [[ "$arg" == "--model" ]] && has_model=true && break; done
    $has_model || { local model; model=$(_get_mprj_model)
        [[ -n "$model" ]] && extra_args=("--model" "$model"); }
    CLAUDE_CONFIG_DIR=~/.claude-mprj \
    CLAUDE_CODE_USE_FOUNDRY=1 \
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
    ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \
    command claude "${extra_args[@]}" "$@"
}

function claude-pro() {
    local extra_args=() has_model=false
    for arg in "$@"; do [[ "$arg" == "--model" ]] && has_model=true && break; done
    if ! $has_model; then
        [[ -z "$_CLAUDE_PRO_MODEL" ]] && {
            local available; available=$(_get_anthropic_models)
            _CLAUDE_PRO_MODEL=$(_select_best_model "$available" "claude-sonnet-4-6")
            printf '  \033[0;36m[claude-pro] modelo: %s\033[0m\n' "$_CLAUDE_PRO_MODEL"; }
        [[ -n "$_CLAUDE_PRO_MODEL" ]] && extra_args=("--model" "$_CLAUDE_PRO_MODEL")
    fi
    CLAUDE_CONFIG_DIR=~/.claude-pessoal \
    command claude "${extra_args[@]}" "$@"
}

alias claude="echo 'Use: claude-mprj  ou  claude-pro'"
alias ch='claude-pro --model claude-haiku-4-5-20251001'
alias cs='claude-pro --model claude-sonnet-4-6'
```

> **Por que `command claude`?**
> Bypassa aliases no Bash/Zsh, chamando o binário diretamente. Sem isso, o alias bloqueador interceptaria a chamada.

**Fish — `~/.config/fish/conf.d/claude.fish`:**

```fish
# --- Claude Code: múltiplas contas ---
set -g _claude_pro_model ""
set -g _claude_model_priority "claude-sonnet-4-6" "claude-haiku-4-5-20251001"

function _get_anthropic_models
    set creds "$HOME/.claude-pessoal/.credentials.json"
    test -f $creds; or return 1
    command -q python3; or return 1
    set token (python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
print(d['claudeAiOauth']['accessToken'])
" $creds 2>/dev/null); or return 1
    curl -sf "https://api.anthropic.com/v1/models" \
        -H "Authorization: Bearer $token" \
        -H "anthropic-version: 2023-06-01" | \
        python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]" 2>/dev/null
end

function _get_mprj_model
    set cache "$HOME/.claude-mprj/.model-cache.json"
    if test -f $cache; and command -q python3
        set age (python3 -c "
import json, sys
from datetime import datetime, timezone
with open(sys.argv[1]) as f:
    d = json.load(f)
dt = datetime.fromisoformat(d['cached_at'].replace('Z','+00:00'))
print(int((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()))
" $cache 2>/dev/null)
        if test -n "$age"; and test (math --scale=0 $age) -lt 604800
            python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" $cache 2>/dev/null; and return
        end
    end

    printf '  \033[1;33m[claude-mprj] Detectando modelo disponivel...\033[0m\n' >&2
    set best "claude-haiku-4-5-20251001"
    for m in $_claude_model_priority
        env CLAUDE_CONFIG_DIR=~/.claude-mprj \
            CLAUDE_CODE_USE_FOUNDRY=1 \
            ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
            ANTHROPIC_FOUNDRY_API_KEY=(cat ~/.secrets/claude-mprj.key 2>/dev/null) \
            command claude --model $m -p "." --print --output-format json >/dev/null 2>&1
        and set best $m; and break
    end
    command -q python3; and python3 -c "
import json, sys
from datetime import datetime, timezone
data = {'model': sys.argv[1], 'cached_at': datetime.now(timezone.utc).isoformat()}
with open(sys.argv[2], 'w') as f:
    json.dump(data, f)
" $best $cache 2>/dev/null
    printf '  \033[0;36m[claude-mprj] modelo: %s (cache 7 dias)\033[0m\n' $best >&2
    echo $best
end

function update-mprj-model
    rm -f "$HOME/.claude-mprj/.model-cache.json"
    env CLAUDE_CONFIG_DIR=~/.claude-mprj \
        CLAUDE_CODE_USE_FOUNDRY=1 \
        ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
        ANTHROPIC_FOUNDRY_API_KEY=(cat ~/.secrets/claude-mprj.key 2>/dev/null) \
        _get_mprj_model > /dev/null
end

function claude-mprj
    set extra_args; set has_model false
    for arg in $argv; test "$arg" = "--model"; and set has_model true; and break; end
    not $has_model; and set model (_get_mprj_model); and test -n "$model"; and set extra_args --model $model
    env CLAUDE_CONFIG_DIR=~/.claude-mprj \
        CLAUDE_CODE_USE_FOUNDRY=1 \
        ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
        ANTHROPIC_FOUNDRY_API_KEY=(cat ~/.secrets/claude-mprj.key 2>/dev/null) \
        command claude $extra_args $argv
end

function claude-pro
    set extra_args; set has_model false
    for arg in $argv; test "$arg" = "--model"; and set has_model true; and break; end
    if not $has_model
        if test -z "$_claude_pro_model"
            set available (_get_anthropic_models)
            set -g _claude_pro_model (
                for m in $_claude_model_priority
                    echo $available | grep -qxF $m; and echo $m; and break
                end
                echo "claude-sonnet-4-6")
            printf '  \033[0;36m[claude-pro] modelo: %s\033[0m\n' $_claude_pro_model
        end
        test -n "$_claude_pro_model"; and set extra_args --model $_claude_pro_model
    end
    env CLAUDE_CONFIG_DIR=~/.claude-pessoal command claude $extra_args $argv
end

function claude; echo 'Use: claude-mprj  ou  claude-pro'; end

abbr --add ch 'claude-pro --model claude-haiku-4-5-20251001'
abbr --add cs 'claude-pro --model claude-sonnet-4-6'
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

# --- Claude Code: Model Routing -----------------------------------------------
$script:ClaudeSessionCache = @{}

$script:ClaudeModelPriority = @(
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001"
)

function Get-AnthropicModels {
    try {
        $creds = Get-Content "$env:USERPROFILE\.claude-pessoal\.credentials.json" -Raw |
            ConvertFrom-Json
        $token = $creds.claudeAiOauth.accessToken
        $r = Invoke-RestMethod 'https://api.anthropic.com/v1/models' `
            -Headers @{ Authorization = "Bearer $token"; 'anthropic-version' = '2023-06-01' }
        return @($r.data | Select-Object -ExpandProperty id)
    } catch { return @() }
}

function Select-BestModel {
    param([string[]]$Available, [string]$Fallback)
    foreach ($m in $script:ClaudeModelPriority) {
        if ($m -in $Available) { return $m }
    }
    return $Fallback
}

function Get-MprjModel {
    $cacheFile = "$env:USERPROFILE\.claude-mprj\.model-cache.json"
    if (Test-Path $cacheFile) {
        try {
            $cache = Get-Content $cacheFile -Raw | ConvertFrom-Json
            if (((Get-Date) - [datetime]$cache.cached_at).TotalDays -lt 7) { return $cache.model }
        } catch {}
    }
    Write-Host '[claude-mprj] Detectando modelo disponivel...' -ForegroundColor Yellow
    $best = 'claude-haiku-4-5-20251001'
    foreach ($m in $script:ClaudeModelPriority) {
        & 'C:\caminho\para\claude.exe' --model $m -p '.' --print --output-format json 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $best = $m; break }
    }
    @{ model = $best; cached_at = (Get-Date -Format 'o') } | ConvertTo-Json | Set-Content $cacheFile
    Write-Host "[claude-mprj] modelo: $best (cache 7 dias)" -ForegroundColor Cyan
    return $best
}

function Update-MprjModel {
    Remove-Item "$env:USERPROFILE\.claude-mprj\.model-cache.json" -ErrorAction SilentlyContinue
    $env:CLAUDE_CONFIG_DIR = "$env:USERPROFILE\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY = '1'
    $env:ANTHROPIC_FOUNDRY_RESOURCE = 'gomas-mok8hc25-eastus2'
    try { Get-MprjModel | Out-Null }
    finally {
        Remove-Item Env:\CLAUDE_CONFIG_DIR, Env:\CLAUDE_CODE_USE_FOUNDRY,
            Env:\ANTHROPIC_FOUNDRY_RESOURCE, Env:\ANTHROPIC_FOUNDRY_API_KEY -ErrorAction SilentlyContinue
    }
}

# --- Claude Code: funções por conta ------------------------------------------

function claude-mprj {
    # ANTHROPIC_FOUNDRY_API_KEY vem das variáveis de ambiente do usuário (Passo 3)
    $env:CLAUDE_CONFIG_DIR          = "$env:USERPROFILE\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY    = '1'
    $env:ANTHROPIC_FOUNDRY_RESOURCE = 'gomas-mok8hc25-eastus2'
    try {
        $extraArgs = @()
        if ('--model' -notin $args) {
            $model = Get-MprjModel
            if ($model) { $extraArgs = @('--model', $model) }
        }
        & 'C:\caminho\para\claude.exe' @extraArgs @args
    } finally {
        Remove-Item Env:\CLAUDE_CONFIG_DIR, Env:\CLAUDE_CODE_USE_FOUNDRY,
            Env:\ANTHROPIC_FOUNDRY_RESOURCE, Env:\ANTHROPIC_FOUNDRY_API_KEY -ErrorAction SilentlyContinue
    }
}

function claude-pro {
    $env:CLAUDE_CONFIG_DIR = "$env:USERPROFILE\.claude-pessoal"
    try {
        $extraArgs = @()
        if ('--model' -notin $args) {
            if (-not $script:ClaudeSessionCache.ContainsKey('pro')) {
                $available = Get-AnthropicModels
                $best = Select-BestModel $available 'claude-sonnet-4-6'
                $script:ClaudeSessionCache['pro'] = $best
                Write-Host "[claude-pro] modelo: $best" -ForegroundColor Cyan
            }
            $model = $script:ClaudeSessionCache['pro']
            if ($model) { $extraArgs = @('--model', $model) }
        }
        & 'C:\caminho\para\claude.exe' @extraArgs @args
    } finally {
        Remove-Item Env:\CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
    }
}

function claude { Write-Host "Use: claude-mprj  ou  claude-pro" -ForegroundColor Yellow }

# aliases rapidos: modelo explicito, sempre claude-pro
function ch { claude-pro --model claude-haiku-4-5-20251001 @args }
function cs { claude-pro --model claude-sonnet-4-6 @args }
```

> Substitua `'C:\caminho\para\claude.exe'` pelo caminho obtido no Passo 2.
> O script `install.ps1` faz isso automaticamente.
>
> **Por que `& 'caminho\claude.exe'`?**
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

### 7.8. Model Routing — Como funciona

Cada função detecta automaticamente o melhor modelo disponível para sua conta.

| Conta | Estratégia | Frequência |
|-------|-----------|-----------|
| `claude-pro` | Consulta `api.anthropic.com/v1/models` (sem custo de tokens) | A cada sessão (cache em memória) |
| `claude-mprj` | Probe via CLI (1 chamada mínima) | A cada 7 dias (cache em arquivo) |

**Prioridade de modelo** (primeiro disponível vence):
```
1. claude-sonnet-4-6
2. claude-haiku-4-5-20251001
```

**Aliases de modelo explícito** (sempre `claude-pro`, ignoram auto-detecção):

| Alias | Modelo | Uso |
|-------|--------|-----|
| `cs`  | `claude-sonnet-4-6` | Tarefas do dia a dia |
| `ch`  | `claude-haiku-4-5-20251001` | Buscas rápidas, leitura de arquivo |

**Forçar re-detecção** (após upgrade no Azure Foundry):

```bash
# Linux / Fish
update-mprj-model
```

```powershell
# Windows PowerShell
Update-MprjModel
```

**Verificar modelo ativo** dentro de uma sessão:
```
/model
```

**Passar modelo explicitamente** (bypassa auto-detecção):
```bash
claude-pro --model claude-haiku-4-5-20251001
claude-mprj --model claude-sonnet-4-6
```

---

## 8. Atualização

> **Backup automático de chaves:** `install.sh` e `install.ps1` agora fazem snapshot timestamped em `~/.claude-md-backups/<ts>/` antes de qualquer operação (chave Foundry, OAuth Pro, `settings.local.json`, `.mcp.json`, `.claude.json`, `.model-cache.json` por conta + dump de `GITLAB_TOKEN` / `POSTMAN_API_KEY`). O instalador preserva todos esses arquivos durante a cópia e ao final restaura qualquer um que tenha sumido. São mantidos os 10 backups mais recentes; os antigos são apagados. Para forçar restore manual: `cp -a ~/.claude-md-backups/<ts>/.secrets/ ~/`.

> **Migração v1→v2 dos blocos de shell:** os heredocs `claude.fish`/`.bashrc`/`.zshrc`/PowerShell `$PROFILE` agora são versionados (`# --- Claude Code: múltiplas contas (v=2) ---` … `# --- end Claude Code multi-conta ---`). Re-execuções do instalador detectam blocos antigos sem versão e perguntam se devem ser substituídos pelo conteúdo atual do repo (que tem fixes como `math --scale=0` e `_claude_mprj_model_priority` separado). O arquivo rc original é copiado para `<rc>.before-update-<ts>` antes da troca. Para forçar a versão atual sem prompt, remova o bloco manualmente e rode `install.sh` de novo.

### Linux

```bash
cd $HOME/workspace/claude-md
git pull

# Rodar o instalador é a forma recomendada — ele faz backup/preserve/restore
bash install.sh

# Atualização manual mínima (sem backup de chaves):
for dir in ~/.claude ~/.claude-mprj ~/.claude-pessoal; do
    [ -d "$dir" ] || continue
    cp CLAUDE.md "$dir/CLAUDE.md"
    cp settings.json "$dir/settings.json"
    cp -r skills/*   "$dir/skills/"
    cp -r commands/* "$dir/commands/"
    # NÃO copiar .mcp.json, settings.local.json, .credentials.json, .claude.json
    echo "Atualizado: $dir"
done
```

---

### Windows

```powershell
cd D:\workspace\claude-md
git pull

# Recomendado: rodar o instalador (snapshot + preserve + restore automático)
.\install.ps1   # escolher modo 2 = atualizar

# Atualização manual mínima (sem backup de chaves):
foreach ($suffix in @("", "-mprj", "-pessoal")) {
    $dir = "$env:USERPROFILE\.claude$suffix"
    if (Test-Path $dir) {
        Copy-Item CLAUDE.md "$dir\CLAUDE.md"
        Copy-Item settings.json "$dir\settings.json"
        Copy-Item -Recurse -Force skills\*   "$dir\skills\"
        Copy-Item -Recurse -Force commands\* "$dir\commands\"
        # NÃO copiar .mcp.json, settings.local.json, .credentials.json, .claude.json
        Write-Host "Atualizado: $dir"
    }
}
```

---

## 9. Teclado ThinkPad T14 Gen 2i — ABNT2 (Garuda Linux / Hyprland)

Não existe layout XKB oficial para este teclado. Solução testada com Hyprland 0.55.2 + keyd.

### Layout físico real

| Tecla física | Keycode | Símbolo |
|---|---|---|
| à direita do L | `<AC10>` | `ç` / `Ç` — br(abnt2) nativo, sem override |
| à direita do `.` | `<AB10>` | `;` / `:` — br(abnt2) nativo, sem override |
| Right Control | KEY_RIGHTCTRL → keyd → `<LSGT>` | `/` / `?` |

> **Por que keyd?** Hyprland intercepta `KEY_RIGHTCTRL` como modificador antes do XKB.
> `modifier_map None` no XKB não resolve — o compositor age antes. keyd converte para
> `KEY_102ND` (`<LSGT>`), keycode neutro sem conflito físico neste teclado.

### Arquivos a criar/restaurar

**`~/.config/hypr/t14br.xkb`**
```xkb
xkb_keymap {
    xkb_keycodes  { include "evdev+aliases(qwerty)" };
    xkb_types     { include "complete" };
    xkb_compat    { include "complete" };
    xkb_symbols   {
        include "pc+br(abnt2)+inet(evdev)"
        key <LSGT> { [slash, question, degree, questiondown] };
    };
    xkb_geometry  { include "pc(pc105)" };
};
```

**`/etc/keyd/default.conf`** (requer sudo)
```ini
[ids]
*

[main]
rightcontrol = 102nd
```

**`~/.config/hypr/hyprland.conf`** — bloco `input`:
```
input {
    kb_file = ~/.config/hypr/t14br.xkb
    # NÃO adicionar kb_layout/kb_variant/kb_model/kb_rules
    # Com kb_file definido, o Hyprland reaplica o layout padrão por cima após reloads
    ...
}
```

### Instalar e ativar

```bash
# 1. Instalar keyd (se não instalado)
paru -S keyd

# 2. Criar /etc/keyd/default.conf com o conteúdo acima (requer sudo)
sudo mkdir -p /etc/keyd
# (copiar o conteúdo manualmente ou via echo)

# 3. Ativar keyd
sudo systemctl enable --now keyd

# 4. Criar ~/.config/hypr/t14br.xkb com o conteúdo acima

# 5. Recarregar Hyprland
hyprctl keyword input:kb_file ~/.config/hypr/t14br.xkb
```

### Reaplicar após mudanças

```bash
hyprctl keyword input:kb_file ~/.config/hypr/t14br.xkb  # mudança no XKB
sudo systemctl restart keyd                              # mudança no keyd
```

---

## 10. Troubleshooting

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

