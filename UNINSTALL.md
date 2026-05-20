# Guia de Desinstalação — Claude Code Multi-Conta

Este documento descreve como desinstalar completamente a configuração de múltiplas contas do Claude Code.

## ⚠️ Aviso Importante

A desinstalação remove:
- **Todas as configurações**: `~/.claude-pessoal/`, `~/.claude-mprj/`, `~/.claude/`
- **Integrações shell**: blocos nos arquivos `.bashrc`, `.zshrc`, `claude.fish`
- **Chaves de API**: `~/.secrets/claude-mprj.key` (Linux)
- **Funções e aliases**: `claude-mprj`, `claude-pro`, `cs`, `ch`

**Um backup automático é criado em `~/.claude-backups/` antes da remoção.**

## Desinstalação Automática (Recomendado)

### Linux / macOS

```bash
cd ~/workspace/claude-md
python3 uninstall.py
```

Ou se estiver usando uv:

```bash
cd ~/workspace/claude-md
uv run uninstall.py
```

### Windows (PowerShell)

```powershell
cd ~\workspace\claude-md
python uninstall.py
```

O script irá:
1. Mostrar preview do que será removido
2. Calcular tamanho total
3. Pedir confirmação
4. Criar backup automático
5. Remover configurações
6. Limpar arquivos shell

## Desinstalação Manual

Se preferir remover manualmente:

### 1. Backup (opcional mas recomendado)

```bash
# Linux/macOS
python3 -c "from installer.backup import backup_secrets; from pathlib import Path; backup_secrets(Path.home(), Path.home() / '.claude-backups')"
```

### 2. Remover diretórios de configuração

```bash
# Linux/macOS
rm -rf ~/.claude-pessoal
rm -rf ~/.claude-mprj
rm -rf ~/.claude
rm -f ~/.secrets/claude-mprj.key  # apenas Linux
```

```powershell
# Windows
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude-pessoal"
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude-mprj"
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude"
```

### 3. Limpar configurações de shell

#### Bash/Zsh (Linux/macOS)

Remova o bloco entre os marcadores nos arquivos `~/.bashrc` e `~/.zshrc`:

```bash
# --- Claude Code: múltiplas contas (v=2) ---
# ... (todo o bloco)
# --- end Claude Code multi-conta ---
```

Comando automatizado:

```bash
sed -i.backup '/# --- Claude Code: múltiplas contas/,/# --- end Claude Code multi-conta ---/d' ~/.bashrc
sed -i.backup '/# --- Claude Code: múltiplas contas/,/# --- end Claude Code multi-conta ---/d' ~/.zshrc
```

#### Fish (Linux/macOS)

```bash
rm ~/.config/fish/conf.d/claude.fish
```

#### PowerShell (Windows)

Remova o bloco entre os marcadores no arquivo de profile:

```powershell
# --- Claude Code: múltiplas contas (v=2) ---
# ... (todo o bloco)
# --- end Claude Code multi-conta ---
```

Locais comuns:
- `$PROFILE` (PowerShell 7+)
- `~\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` (Windows PowerShell)

### 4. Recarregar shell

```bash
# Linux/macOS
source ~/.bashrc  # ou ~/.zshrc
# ou simplesmente reinicie o terminal
```

```powershell
# Windows
. $PROFILE
# ou reinicie o PowerShell
```

## Restauração a Partir do Backup

Se precisar restaurar após desinstalação:

```bash
# Listar backups disponíveis
ls -lh ~/.claude-backups/

# Restaurar do backup mais recente
BACKUP_DIR=$(ls -t ~/.claude-backups/ | head -1)
cp -r ~/.claude-backups/$BACKUP_DIR/* ~/
```

Os backups contêm:
- Arquivos de configuração (`.credentials.json`, `settings.local.json`, etc.)
- Snapshot de variáveis de ambiente (`env.snapshot`)
- Estrutura completa dos diretórios `.claude*`

## Verificação Pós-Desinstalação

```bash
# Verificar diretórios removidos
ls -la ~/.claude* 2>/dev/null || echo "✓ Diretórios removidos"

# Verificar funções shell
type claude-mprj 2>/dev/null && echo "✗ Ainda presente" || echo "✓ Removido"
type claude-pro 2>/dev/null && echo "✗ Ainda presente" || echo "✓ Removido"

# Verificar aliases
alias | grep -E "(claude|cs|ch)" && echo "✗ Aliases presentes" || echo "✓ Aliases removidos"
```

## Desinstalar Apenas Uma Conta

Se quiser manter uma conta e remover apenas a outra:

### Remover apenas MPRJ (manter pessoal)

```bash
rm -rf ~/.claude-mprj
rm -f ~/.secrets/claude-mprj.key  # Linux

# Editar manualmente .bashrc/.zshrc/claude.fish:
# - Remover função claude-mprj
# - Remover variáveis/funções relacionadas ao MPRJ
# - Manter função claude-pro
```

### Remover apenas pessoal (manter MPRJ)

```bash
rm -rf ~/.claude-pessoal

# Editar manualmente .bashrc/.zshrc/claude.fish:
# - Remover função claude-pro
# - Remover aliases cs/ch
# - Manter função claude-mprj
```

## FAQ

### Os arquivos `.claude.json` e `.credentials.json` são removidos?

Sim, eles ficam dentro dos diretórios `~/.claude-pessoal/` e `~/.claude-mprj/` que são completamente removidos. **Um backup é criado automaticamente antes da remoção.**

### O que acontece com o executável `claude`?

O executável `claude` instalado pelo npm/homebrew **não é removido**. Apenas as configurações, funções shell e aliases são removidos.

Para remover o executável:

```bash
# npm
npm uninstall -g @anthropic-ai/claude-code

# Homebrew
brew uninstall claude-code
```

### Os backups são removidos?

Não. Os backups em `~/.claude-backups/` são preservados. Para limpá-los:

```bash
rm -rf ~/.claude-backups/
```

### Preciso desinstalar antes de reinstalar?

**Não.** O instalador faz upgrade automático preservando secrets. Só desinstale se quiser remover completamente ou resetar tudo.

## Suporte

- **Issues**: https://github.com/anthropics/claude-code/issues
- **Docs**: https://docs.anthropic.com/claude/docs/claude-code

---

**Última atualização:** 2026-05-20
