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

## .env — Infisical (por projeto)

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

## Token GitLab — Criação e Permissões

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

## Variáveis de Ambiente para MCP GitLab

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
