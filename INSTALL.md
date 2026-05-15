# Instalação e Configuração do Claude Code

Este guia cobre instalação da configuração global e setup de múltiplas contas (MPRJ/Foundry + pessoal PRO).

**Ambientes:**
- **Windows 11**: `D:\workspace\claude-md`
- **Linux Arch (Garuda)**: `$HOME/workspace/claude-md`

---

## Índice

1. [Instalação da Configuração Global](#1-instalação-da-configuração-global)
2. [Token GitLab](#2-token-gitlab)
3. [Variáveis de Ambiente para MCP GitLab](#3-variáveis-de-ambiente-para-mcp-gitlab)
4. [.env — Infisical (por projeto)](#4-env--infisical-por-projeto)
5. [MCP Servers](#5-mcp-servers)
6. [Múltiplas Contas (MPRJ + Pessoal)](#6-múltiplas-contas-mprj--pessoal)
7. [Atualização](#7-atualização)

---

## 1. Instalação da Configuração Global

### Linux (Garuda / Arch)

```bash
# Navegar até o repositório
cd $HOME/workspace/claude-md

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

### Windows 11 (PowerShell)

```powershell
# Navegar até o repositório
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

## 2. Token GitLab

Acesse: `https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens`

### Configurações do token

| Campo       | Valor recomendado                          |
|-------------|---------------------------------------------|
| Token name  | `claude-code-mprj`                          |
| Expiration  | 1 ano (renovar no vencimento)               |
| Scopes      | ver tabela abaixo                           |

### Scopes — o máximo que boas práticas permitem

| Scope              | Marcar | Motivo                                                       |
|--------------------|--------|--------------------------------------------------------------|
| `api`              | ✅     | Acesso completo à API REST — projetos, MRs, issues, pipelines, registry, perfil |
| `read_repository`  | ✅     | Clonar repositórios privados via HTTPS (`api` não cobre git over HTTPS) |
| `write_repository` | ✅     | Push via HTTPS — necessário para o Claude Code fazer push    |
| `read_registry`    | ✅     | Pull de imagens do Container Registry                        |
| `write_registry`   | ✅     | Push de imagens ao Container Registry                        |
| `read_user`        | ❌     | Redundante — já coberto pelo `api`                           |
| `create_runner`    | ❌     | Desnecessário — não registramos runners via Claude           |
| `manage_runner`    | ❌     | Desnecessário                                                |
| `ai_features`      | ❌     | Recursos GitLab AI — não utilizado                           |
| `k8s_proxy`        | ❌     | Proxy Kubernetes — não utilizado                             |
| `sudo`             | ❌     | Impersonar outros usuários — nunca conceder                  |

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

## 3. Variáveis de Ambiente para MCP GitLab

### Linux — `~/.bashrc` ou `~/.zshrc`

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_URL="https://gitlab-dti.mprj.mp.br"
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

## 4. .env — Infisical (por projeto)

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

## 5. MCP Servers

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

## 6. Múltiplas Contas (MPRJ + Pessoal)

Permite usar conta corporativa (Microsoft Foundry / MPRJ) e conta pessoal PRO na mesma máquina,
sem logout manual. Cada conta tem configuração, credenciais e sessão totalmente isoladas.

### Como funciona

O Claude Code usa `~/.claude` (Linux) ou `%USERPROFILE%\.claude` (Windows) para armazenar tudo.
A variável `CLAUDE_CONFIG_DIR` permite apontar para diretórios diferentes por conta.

- **Conta MPRJ (Microsoft Foundry)**: autentica via API Key — sem `/login`, sem browser
- **Conta pessoal PRO**: autentica via OAuth normal com `/login`

---

### 6.1. Linux (Garuda / Arch)

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
echo 'export ANTHROPIC_FOUNDRY_API_KEY="sk-ant-..."' > ~/.secrets/claude-mprj.env
chmod 600 ~/.secrets/claude-mprj.env
```

#### Passo 3: Adicionar funções ao shell

Edite `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh / Garuda padrão):

```bash
# --- Claude Code: múltiplas contas ---

# Conta corporativa (MPRJ / Microsoft Foundry)
# Autenticação via API Key — não usa /login, não abre browser
function claude-mprj() {
    source ~/.secrets/claude-mprj.env
    CLAUDE_CONFIG_DIR=~/.claude-mprj \
    CLAUDE_CODE_USE_FOUNDRY=1 \
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
    command claude "$@"
    unset ANTHROPIC_FOUNDRY_API_KEY
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

Recarregue:

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

type claude-pro
# Saída esperada: claude-pro is a function
```

---

### 6.2. Windows 11

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

Get-Command claude-pro
# Esperado: CommandType = Function
```

#### Passo 7: Uso diário

```powershell
claude-mprj    # conta MPRJ / Foundry
claude-pro     # conta pessoal PRO
```

---

### 6.3. Alternativa Windows — CMD (Prompt de Comando)

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

### 6.4. Comportamento por tipo de configuração

| Configuração                                  | Isolada por conta? | Observação                               |
|-----------------------------------------------|--------------------|------------------------------------------|
| Credenciais / sessão OAuth                    | ✅ Sim              | Cada diretório tem seu próprio login     |
| API Key Foundry (`ANTHROPIC_FOUNDRY_API_KEY`) | ✅ Sim              | Injetada só na função `claude-mprj`      |
| `CLAUDE.md` global (`~/.claude/`)             | ✅ Sim              | Separado por conta                       |
| `CLAUDE.md` de projeto (no repo)              | ❌ Não              | Fica no repo, compartilhado entre contas |
| MCP servers                                   | ✅ Sim              | Configurar separadamente em cada conta   |
| Histórico de sessões                          | ✅ Sim              | Totalmente isolado                       |

---

### 6.5. Configuração por projeto (opcional)

Para fixar uma conta específica por repositório, adicione ao `.env` na raiz do projeto:

```bash
# Linux
CLAUDE_CONFIG_DIR=/home/welington/.claude-mprj
```

```env
# Windows
CLAUDE_CONFIG_DIR=C:\Users\welington.souza\.claude-mprj
```

---

### 6.6. Verificando a conta ativa

Dentro de qualquer sessão do Claude Code:

```
/status
```

Ou no terminal:

```bash
# Linux
echo $CLAUDE_CONFIG_DIR

# Windows PowerShell
echo $env:CLAUDE_CONFIG_DIR
```

---

### 6.7. Estrutura final de diretórios

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
└── claude-mprj.env       # API Key (chmod 600, fora do controle de versão)
```

---

## 7. Atualização

Para atualizar a configuração global depois de mudar este repositório:

### Linux

```bash
cd $HOME/workspace/claude-md

# Re-executar o bloco de cópia
cp CLAUDE.md ~/.claude/CLAUDE.md
cp settings.json ~/.claude/settings.json
cp -r skills/* ~/.claude/skills/
cp -r commands/* ~/.claude/commands/

# Se usar múltiplas contas, atualizar ambas
cp CLAUDE.md ~/.claude-mprj/CLAUDE.md
cp settings.json ~/.claude-mprj/settings.json
cp -r skills/* ~/.claude-mprj/skills/
cp -r commands/* ~/.claude-mprj/commands/

cp CLAUDE.md ~/.claude-pessoal/CLAUDE.md
cp settings.json ~/.claude-pessoal/settings.json
cp -r skills/* ~/.claude-pessoal/skills/
cp -r commands/* ~/.claude-pessoal/commands/
```

### Windows

```powershell
cd D:\workspace\claude-md

# Re-executar o bloco de cópia
Copy-Item CLAUDE.md "$env:USERPROFILE\.claude\CLAUDE.md"
Copy-Item settings.json "$env:USERPROFILE\.claude\settings.json"
Copy-Item -Recurse -Force skills\* "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force commands\* "$env:USERPROFILE\.claude\commands\"

# Se usar múltiplas contas, atualizar ambas
Copy-Item CLAUDE.md "$env:USERPROFILE\.claude-mprj\CLAUDE.md"
Copy-Item settings.json "$env:USERPROFILE\.claude-mprj\settings.json"
Copy-Item -Recurse -Force skills\* "$env:USERPROFILE\.claude-mprj\skills\"
Copy-Item -Recurse -Force commands\* "$env:USERPROFILE\.claude-mprj\commands\"

Copy-Item CLAUDE.md "$env:USERPROFILE\.claude-pessoal\CLAUDE.md"
Copy-Item settings.json "$env:USERPROFILE\.claude-pessoal\settings.json"
Copy-Item -Recurse -Force skills\* "$env:USERPROFILE\.claude-pessoal\skills\"
Copy-Item -Recurse -Force commands\* "$env:USERPROFILE\.claude-pessoal\commands\"
```
