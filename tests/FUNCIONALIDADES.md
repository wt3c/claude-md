# Funcionalidades dos Instaladores — Mapeamento Completo

Este documento mapeia todas as funcionalidades de `install.sh` e `install.ps1` que precisam ser testadas para garantir que a migração para Python mantenha o comportamento idêntico.

## 1. Backup e Restore de Secrets

### Funcionalidades
- **Backup antes da instalação**: Cria snapshot timestamped em `~/.claude-md-backups/<timestamp>/`
- **Arquivos sensíveis preservados**:
  - `~/.secrets/claude-mprj.key` (Linux apenas)
  - `~/.claude/settings.local.json`
  - `~/.claude/.mcp.json`
  - `~/.claude-mprj/.credentials.json`
  - `~/.claude-mprj/.claude.json`
  - `~/.claude-mprj/.model-cache.json`
  - `~/.claude-mprj/settings.local.json`
  - `~/.claude-mprj/.mcp.json`
  - `~/.claude-pessoal/.credentials.json`
  - `~/.claude-pessoal/.claude.json`
  - `~/.claude-pessoal/.model-cache.json`
  - `~/.claude-pessoal/settings.local.json`
  - `~/.claude-pessoal/.mcp.json`
- **Snapshot de env vars**: Extrai `GITLAB_TOKEN`, `GITLAB_URL`, `POSTMAN_API_KEY`, `ANTHROPIC_FOUNDRY_API_KEY` dos arquivos rc e salva em `env.snapshot`
- **Restore pós-instalação**: Restaura arquivos ausentes do backup mais recente
- **Limpeza de backups antigos**: Mantém apenas os 10 backups mais recentes
- **Permissões**: Backup dir tem chmod 700

### Comportamentos a testar
- ✅ Backup cria diretório timestamped
- ✅ Todos os arquivos sensíveis existentes são copiados
- ✅ Estrutura de diretórios preservada (paths relativos ao $HOME)
- ✅ env.snapshot contém variáveis corretas
- ✅ Restore não sobrescreve arquivos já existentes
- ✅ Restore copia apenas arquivos ausentes
- ✅ Mantém exatamente 10 backups (remove os mais antigos)
- ✅ Chmod 700 no diretório de backup

---

## 2. Verificação de Pré-requisitos

### Funcionalidades
- **Git**: Verifica presença e exibe versão
- **Node.js**: Verifica versão ≥ 18
- **Claude Code**: Verifica instalação global
- **Falhas**: Script aborta com erro se algum pré-requisito faltar

### Comportamentos a testar
- ✅ Detecta git ausente → erro e exit
- ✅ Detecta git presente → exibe versão e continua
- ✅ Detecta node ausente → erro com instrução de instalação
- ✅ Detecta node < v18 → erro com instrução de atualização
- ✅ Detecta node ≥ v18 → exibe versão e continua
- ✅ Detecta claude ausente → erro com instrução npm install
- ✅ Detecta claude presente → exibe versão e continua

---

## 3. Atualização do Repositório

### Funcionalidades
- **Git pull**: Tenta `git pull --ff-only` se remote configurado
- **Sem remote**: Aviso e usa versão local
- **Falha no pull**: Aviso e continua com versão local

### Comportamentos a testar
- ✅ Remote configurado → git pull executado
- ✅ Sem remote → aviso e continua
- ✅ Pull falha → aviso e continua
- ✅ Pull sucesso → mensagem de sucesso

---

## 4. Instalação de Arquivos em Diretórios

### Funcionalidades
- **Diretórios criados**:
  - `~/.claude/` (ou equivalente Windows)
  - `~/.claude-mprj/`
  - `~/.claude-pessoal/`
  - Subdiretórios: `tasks/archive/`, `skills/`, `commands/`
- **Arquivos sempre sobrescritos**:
  - `CLAUDE.md`
  - `settings.json`
  - `skills/*` (recursivo)
  - `commands/*` (recursivo)
- **Arquivos preservados se já existirem**:
  - `.mcp.json`
  - `settings.local.json`
  - `.credentials.json`
  - `.claude.json`
  - `.model-cache.json`
  - `tasks/todo.md`
  - `tasks/lessons.md`
  - `tasks/decisions.md`
- **Arquivo criado**: `audit.log` (touch)

### Comportamentos a testar
- ✅ Cria estrutura de diretórios completa
- ✅ Copia CLAUDE.md e settings.json (sempre sobrescreve)
- ✅ Copia skills/ e commands/ recursivamente
- ✅ Copia tasks/*.md apenas se não existirem
- ✅ Preserva .mcp.json existente (aviso se existir)
- ✅ Preserva settings.local.json existente
- ✅ Preserva .credentials.json existente
- ✅ Preserva .claude.json existente
- ✅ Preserva .model-cache.json existente
- ✅ Cria audit.log vazio

---

## 5. Configuração de Shell

### Funcionalidades
- **Versionamento**: Blocos marcados com `v=2` no marker
- **Detecção de versão antiga**: Regex `^# --- Claude Code: múltiplas contas` sem versão
- **Migração v1→v2**: Backup do rc (`<rc>.before-update-<timestamp>`) e substituição
- **Shells suportados**:
  - Bash: `~/.bashrc`
  - Zsh: `~/.zshrc`
  - Fish: `~/.config/fish/conf.d/claude.fish`
  - PowerShell: `$PROFILE`
- **Blocos inseridos**:
  - Funções `claude-mprj` e `claude-pro`
  - Model routing (`_get_mprj_model`, `_get_anthropic_models`, etc)
  - Alias bloqueador `claude="echo 'Use: claude-mprj ou claude-pro'"`
  - Aliases rápidos `ch` e `cs`
- **Markers**:
  - Início: `# --- Claude Code: múltiplas contas (v=2) ---`
  - Fim: `# --- end Claude Code multi-conta ---`
  - Legacy: `# --- Claude Code: múltiplas contas ---` (sem versão)

### Comportamentos a testar
- ✅ Detecta bloco v2 já presente → não duplica
- ✅ Detecta bloco v1 → pergunta se substitui
- ✅ Usuário aceita migração → backup + substitui bloco
- ✅ Usuário rejeita migração → mantém bloco antigo
- ✅ Sem bloco → insere bloco novo
- ✅ Bash: append ao ~/.bashrc
- ✅ Zsh: append ao ~/.zshrc
- ✅ Fish: sobrescreve ~/.config/fish/conf.d/claude.fish (não append)
- ✅ PowerShell: append ao $PROFILE
- ✅ PowerShell: substitui placeholder CLAUDE_EXE_PATH pelo caminho real
- ✅ Backup tem timestamp no nome

---

## 6. Configuração de API Keys e Tokens

### 6.1. ANTHROPIC_FOUNDRY_API_KEY

**Linux:**
- Armazena em `~/.secrets/claude-mprj.key` (arquivo texto puro, sem newline final)
- Chmod 600 no arquivo
- Chmod 700 no diretório ~/.secrets/

**Windows:**
- Armazena em variável de ambiente do usuário (persistente)
- `[Environment]::SetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY", "...", "User")`

**Comportamentos comuns:**
- ✅ Detecta chave existente → mostra últimos 4 chars mascarados
- ✅ Pergunta se mantém → preserva chave existente
- ✅ Usuário fornece nova chave → remove aspas/espaços antes de salvar
- ✅ Input vazio + chave existente → mantém antiga
- ✅ Input vazio + sem chave → aviso

### 6.2. GITLAB_TOKEN e GITLAB_URL

**Linux (Bash/Zsh):**
- Append a `~/.bashrc` ou `~/.zshrc`: `export GITLAB_TOKEN="..."`
- Append a Fish: `set -x GITLAB_TOKEN "..."`
- Sempre adiciona `GITLAB_URL="https://gitlab-dti.mprj.mp.br"`

**Windows:**
- Variável de ambiente do usuário (persistente)

**Comportamentos:**
- ✅ Detecta token existente em qualquer rc → mostra últimos 4 chars
- ✅ Pergunta se mantém → preserva token
- ✅ Usuário fornece novo token → adiciona ao rc do shell atual
- ✅ Input vazio → aviso

### 6.3. POSTMAN_API_KEY

**Mesmo comportamento de GITLAB_TOKEN:**
- ✅ Detecta em rc existente
- ✅ Pergunta se mantém
- ✅ Adiciona ao rc ou env var (Windows)

---

## 7. Instalação de MCP Servers

### Funcionalidades
- **Comando**: `claude mcp add --scope user <name> -- <command>`
- **Detecção de MCP já instalado**: `claude mcp list` + grep
- **MCPs instalados**:
  - `filesystem`: `npx -y @modelcontextprotocol/server-filesystem "$HOME"`
  - `memory`: `npx -y @modelcontextprotocol/server-memory`
  - `gitlab`: `npx -y @modelcontextprotocol/server-gitlab`
  - `postman`: `npx -y @postman/postman-mcp-server`
- **Comportamento**: Pula se já instalado (aviso)

### Comportamentos a testar
- ✅ MCP não instalado → instala com sucesso
- ✅ MCP já instalado → pula e avisa
- ✅ Todos os 4 MCPs são instalados
- ✅ Mensagem informativa sobre postgres e playwright (por projeto)

---

## 8. Fluxo Principal (Main)

### Linux (install.sh)
1. Banner
2. `check_prereqs`
3. `update_repo`
4. `backup_secrets`
5. Pergunta múltiplas contas (default: y)
6. `install_to_dir ~/.claude`
7. Se multi-conta:
   - `install_to_dir ~/.claude-mprj`
   - `install_to_dir ~/.claude-pessoal`
   - `configure_api_key`
   - `configure_shell`
   - `configure_gitlab`
8. Pergunta instalar MCPs (default: y)
9. Se sim:
   - `install_mcps`
   - `configure_postman_key`
10. `restore_secrets`
11. Resumo final

### Windows (install.ps1)
1. Banner
2. `Get-ClaudeExe` (prereqs)
3. `Update-Repo`
4. `Backup-Secrets`
5. Pergunta modo: 1=fresh install, 2=update
6. Se modo 2:
   - `Update-AllDirs`
   - `Restore-Secrets`
   - Exit
7. Pergunta múltiplas contas (default: y)
8. `Install-ToDir $env:USERPROFILE\.claude`
9. Se multi-conta:
   - `Install-ToDir ...\.claude-mprj`
   - `Install-ToDir ...\.claude-pessoal`
   - `Set-FoundryApiKey`
   - `Set-GitLabToken`
   - Pergunta configurar Profile (default: y)
   - Se sim: `Set-ProfileFunctions`
10. Pergunta instalar MCPs (default: y)
11. Se sim:
    - `Install-MCPs`
    - `Set-PostmanApiKey`
12. `Restore-Secrets`
13. Resumo final

### Comportamentos a testar
- ✅ Fluxo completo sem erros (multi-conta)
- ✅ Fluxo completo sem erros (single account)
- ✅ Fluxo de update (Windows modo 2)
- ✅ Abort em qualquer pré-requisito falhando
- ✅ Mensagens de progresso corretas
- ✅ Resumo final com próximos passos

---

## 9. Interação com Usuário

### Funções de input
- **Linux**: `ask()`, `ask_yn()`
- **Windows**: `Ask-Input`, `Ask-YesNo`

### Defaults
- Múltiplas contas: `y`
- Instalar MCPs: `y`
- Manter chave/token existente: `y`
- Substituir bloco shell antigo: `y`
- Shell choice (Linux): `1` (Bash)

### Comportamentos a testar
- ✅ Input vazio usa default
- ✅ Y/y/yes aceita em yes/no
- ✅ N/n/no rejeita em yes/no
- ✅ Input case-insensitive

---

## 10. Casos de Borda

### Arquivo/diretório já existente
- ✅ Diretório já existe → não falha, usa existente
- ✅ Arquivo sobrescrevível já existe → sobrescreve sem aviso
- ✅ Arquivo preservável já existe → preserva e avisa

### Git
- ✅ Sem remote configurado → aviso, usa local
- ✅ Pull falha → aviso, usa local
- ✅ Não é um repositório git → ? (testar)

### Shell
- ✅ Arquivo rc não existe → cria antes de inserir
- ✅ Bloco de shell corrompido → ? (testar remoção)
- ✅ Múltiplos blocos legacy → remove o primeiro encontrado

### API Keys
- ✅ Input com aspas `"sk-ant-..."` → remove aspas
- ✅ Input com espaços ` sk-ant-... ` → trim
- ✅ Input vazio → preserva existente ou avisa

### MCPs
- ✅ `claude mcp list` falha → ? (verificar tratamento de erro)
- ✅ `claude mcp add` falha → ? (verificar tratamento de erro)

---

## 11. Cobertura de Código Esperada

### Funções críticas (100% de cobertura obrigatória)
- `backup_secrets` / `Backup-Secrets`
- `restore_secrets` / `Restore-Secrets`
- `check_prereqs` / `Get-ClaudeExe`
- `install_to_dir` / `Install-ToDir`
- `configure_shell` / `Set-ProfileFunctions`
- `configure_api_key` / `Set-FoundryApiKey`
- `configure_gitlab` / `Set-GitLabToken`
- `install_mcps` / `Install-MCPs`

### Funções auxiliares
- `_sensitive_files` / `Get-SensitiveFiles`
- `_copy_into_backup`
- `_snapshot_env_vars` / `Backup-EnvVars`
- `_remove_shell_block` / `Remove-ProfileBlock`
- `ask`, `ask_yn` / `Ask-Input`, `Ask-YesNo`

### Fluxo principal
- `main` / `Main`

---

## 12. Estrutura de Testes Proposta

```
tests/
├── __init__.py
├── conftest.py              # Fixtures globais
├── test_backup_restore.py   # Testes de backup/restore
├── test_prereqs.py          # Testes de pré-requisitos
├── test_install_files.py    # Testes de instalação de arquivos
├── test_shell_config.py     # Testes de configuração de shell
├── test_api_keys.py         # Testes de API keys e tokens
├── test_mcp.py              # Testes de MCP installation
├── test_integration.py      # Testes de integração (fluxo completo)
└── fixtures/                # Dados de teste
    ├── mock_repo/
    ├── mock_home/
    └── expected_outputs/
```

---

## 13. Estratégia de Testes

### Testes unitários
- Testar funções isoladas com mocks
- Validar lógica de decisão (if/else)
- Validar transformações de dados

### Testes de integração
- Executar scripts reais em ambiente isolado (temp dirs)
- Simular inputs do usuário via stdin
- Validar estado final do filesystem

### Testes parametrizados
- Testar múltiplos shells (bash/zsh/fish/powershell)
- Testar múltiplos cenários de input
- Testar múltiplas plataformas (Linux/Windows via subprocess)

### Mocks necessários
- `git` command
- `node` command
- `claude` command
- `curl` (para API Anthropic em model routing)
- User input (stdin)
- Filesystem (opcional, usar temp dirs reais é melhor)

---

**Objetivo:** 100% de cobertura comportamental — todos os caminhos de execução testados, garantindo que a versão Python seja funcionalmente idêntica.
