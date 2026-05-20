"""
Configuração de shell (bash, zsh, fish, powershell) com versionamento.

Equivalente a _append_bash_zsh(), _append_fish(), Set-ProfileFunctions().
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from installer.platform import ShellType, get_rc_file

SHELL_BLOCK_VERSION = "2"
MARKER = "# --- Claude Code: múltiplas contas (v=2) ---"
MARKER_LEGACY_RE = r"^# --- Claude Code: múltiplas contas"
MARKER_END = "# --- end Claude Code multi-conta ---"


def detect_shell_block_version(rc_file: Path) -> Optional[str]:
    """
    Detecta versão do bloco shell ou None se não existir.

    Returns:
        "v2" | "v1" | None
    """
    if not rc_file.exists():
        return None

    content = rc_file.read_text()

    if MARKER in content:
        return "v2"

    if re.search(MARKER_LEGACY_RE, content, re.MULTILINE):
        return "v1"

    return None


def remove_shell_block(rc_file: Path) -> Path:
    """
    Remove bloco shell e cria backup.

    Equivalente a _remove_shell_block() do install.sh (linhas 222-236).

    Args:
        rc_file: Arquivo rc a modificar

    Returns:
        Path do arquivo de backup criado
    """
    if not rc_file.exists():
        return None  # type: ignore[return-value]

    # Backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = rc_file.parent / f"{rc_file.name}.before-update-{timestamp}"
    shutil.copy2(rc_file, backup)

    # Remover bloco
    lines = rc_file.read_text().splitlines()
    new_lines = []
    in_block = False

    for line in lines:
        if re.match(MARKER_LEGACY_RE, line):
            in_block = True
            continue
        if in_block and line.startswith(MARKER_END):
            in_block = False
            continue
        if not in_block:
            new_lines.append(line)

    rc_file.write_text("\n".join(new_lines) + "\n")

    return backup


def install_shell_block(
    shell: ShellType, home: Path, *, replace_legacy: bool = True
) -> Path:
    """
    Instala bloco shell v2 (bash, zsh, fish, powershell).

    Equivalente a:
    - _append_bash_zsh() do install.sh (linhas 238-382)
    - _append_fish() do install.sh (linhas 384-529)
    - Set-ProfileFunctions() do install.ps1 (linhas 249-399)

    Args:
        shell: Tipo de shell
        home: Diretório HOME
        replace_legacy: Se True, remove bloco v1 antes de adicionar v2

    Returns:
        Path do arquivo rc modificado
    """
    rc_file = get_rc_file(shell, home)

    # Criar arquivo se não existir
    rc_file.parent.mkdir(parents=True, exist_ok=True)
    if not rc_file.exists():
        rc_file.touch()

    # Detectar versão existente
    version = detect_shell_block_version(rc_file)

    if version == "v2":
        # Já tem v2, pular
        return rc_file

    if version == "v1" and replace_legacy:
        # Remover v1
        remove_shell_block(rc_file)

    # Adicionar v2
    block_content = _get_shell_block_content(shell)

    if shell == "fish":
        # Fish: sobrescrever arquivo completo
        rc_file.write_text(block_content)
    else:
        # Bash/Zsh/PowerShell: append
        with rc_file.open("a") as f:
            f.write("\n" + block_content + "\n")

    return rc_file


def _get_shell_block_content(shell: ShellType) -> str:
    """
    Retorna conteúdo do bloco shell v2.

    Equivalente aos heredocs SHELLBLOCK/FISHBLOCK e here-string PowerShell.
    """
    if shell in ["bash", "zsh"]:
        return _BASH_ZSH_BLOCK

    elif shell == "fish":
        return _FISH_BLOCK

    elif shell == "powershell":
        return _POWERSHELL_BLOCK

    return ""


# Bloco Bash/Zsh (install.sh linhas 257-380)
_BASH_ZSH_BLOCK = """
# --- Claude Code: múltiplas contas (v=2) ---

# --- Claude Code: Model Routing -----------------------------------------------
_CLAUDE_PRO_MODEL=""

_claude_model_priority=("claude-sonnet-4-6" "claude-haiku-4-5-20251001")
_claude_mprj_model_priority=("claude-sonnet-4-5")

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
    curl -sf "https://api.anthropic.com/v1/models" \\
        -H "Authorization: Bearer $token" \\
        -H "anthropic-version: 2023-06-01" | \\
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
        local age ts
        ts=$(python3 -c "
import json, sys
from datetime import datetime, timezone
with open(sys.argv[1]) as f:
    d = json.load(f)
dt = datetime.fromisoformat(d['cached_at'].replace('Z','+00:00'))
print(int(dt.astimezone(timezone.utc).timestamp()))
" "$cache" 2>/dev/null || echo 0)
        age=$(( $(date +%s) - ts ))
        if (( age < 604800 )); then
            python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" "$cache" 2>/dev/null && return
        fi
    fi

    printf '  \\033[1;33m[claude-mprj] Detectando modelo disponivel...\\033[0m\\n' >&2
    local best="claude-sonnet-4-5"
    for m in "${_claude_mprj_model_priority[@]}"; do
        CLAUDE_CONFIG_DIR="$HOME/.claude-mprj" \\
        CLAUDE_CODE_USE_FOUNDRY=1 \\
        ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \\
        ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \\
        command claude --model "$m" -p "." --print --output-format json >/dev/null 2>&1 \\
            && best="$m" && break
    done

    if command -v python3 &>/dev/null; then
        python3 -c "
import json, sys
from datetime import datetime, timezone
data = {'model': sys.argv[1], 'cached_at': datetime.now(timezone.utc).isoformat()}
with open(sys.argv[2], 'w') as f:
    json.dump(data, f)
" "$best" "$cache" 2>/dev/null
    fi
    printf '  \\033[0;36m[claude-mprj] modelo: %s (cache 7 dias)\\033[0m\\n' "$best" >&2
    echo "$best"
}

update-mprj-model() {
    rm -f "$HOME/.claude-mprj/.model-cache.json"
    CLAUDE_CONFIG_DIR="$HOME/.claude-mprj" \\
    CLAUDE_CODE_USE_FOUNDRY=1 \\
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \\
    ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \\
    _get_mprj_model > /dev/null
}

# --- Claude Code: funções por conta ------------------------------------------

function claude-mprj() {
    local extra_args=() has_model=false
    for arg in "$@"; do [[ "$arg" == "--model" ]] && has_model=true && break; done

    if ! $has_model; then
        local model; model=$(_get_mprj_model)
        [[ -n "$model" ]] && extra_args=("--model" "$model")
    fi
    CLAUDE_CONFIG_DIR=~/.claude-mprj \\
    CLAUDE_CODE_USE_FOUNDRY=1 \\
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \\
    ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \\
    command claude "${extra_args[@]}" "$@"
}

function claude-pro() {
    local extra_args=() has_model=false
    for arg in "$@"; do [[ "$arg" == "--model" ]] && has_model=true && break; done

    if ! $has_model; then
        if [[ -z "$_CLAUDE_PRO_MODEL" ]]; then
            local available; available=$(_get_anthropic_models)
            _CLAUDE_PRO_MODEL=$(_select_best_model "$available" "claude-sonnet-4-6")
            printf '  \\033[0;36m[claude-pro] modelo: %s\\033[0m\\n' "$_CLAUDE_PRO_MODEL"
        fi
        [[ -n "$_CLAUDE_PRO_MODEL" ]] && extra_args=("--model" "$_CLAUDE_PRO_MODEL")
    fi
    CLAUDE_CONFIG_DIR=~/.claude-pessoal \\
    command claude "${extra_args[@]}" "$@"
}

alias claude="echo 'Use: claude-mprj  ou  claude-pro'"
alias ch='claude-pro --model claude-haiku-4-5-20251001'
alias cs='claude-pro --model claude-sonnet-4-6'
# --- end Claude Code multi-conta ---
"""

# Bloco Fish (install.sh linhas 404-528)
_FISH_BLOCK = """# --- Claude Code: múltiplas contas (v=2) ---

# --- Claude Code: Model Routing -----------------------------------------------
set -g _claude_pro_model ""
set -g _claude_model_priority "claude-sonnet-4-6" "claude-haiku-4-5-20251001"
set -g _claude_mprj_model_priority "claude-sonnet-4-5"

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
    curl -sf "https://api.anthropic.com/v1/models" \\
        -H "Authorization: Bearer $token" \\
        -H "anthropic-version: 2023-06-01" | \\
        python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]" 2>/dev/null
end

function _select_best_model
    set available $argv[1]
    set fallback $argv[2]
    for m in $_claude_model_priority
        echo $available | grep -qxF $m; and echo $m; and return
    end
    echo $fallback
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
print((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds())
" $cache 2>/dev/null)
        if test -n "$age"; and test (math --scale=0 $age) -lt 604800
            python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" $cache 2>/dev/null; and return
        end
    end

    printf '  \\033[1;33m[claude-mprj] Detectando modelo disponivel...\\033[0m\\n' >&2
    set best "claude-sonnet-4-5"
    for m in $_claude_mprj_model_priority
        set -lx CLAUDE_CONFIG_DIR ~/.claude-mprj
        set -lx CLAUDE_CODE_USE_FOUNDRY 1
        set -lx ANTHROPIC_FOUNDRY_RESOURCE "gomas-mok8hc25-eastus2"
        set -lx ANTHROPIC_FOUNDRY_API_KEY (cat ~/.secrets/claude-mprj.key 2>/dev/null)
        command claude --model $m -p "." --print --output-format json >/dev/null 2>&1
        and set best $m; and break
    end

    if command -q python3
        python3 -c "
import json, sys
from datetime import datetime, timezone
data = {'model': sys.argv[1], 'cached_at': datetime.now(timezone.utc).isoformat()}
with open(sys.argv[2], 'w') as f:
    json.dump(data, f)
" $best $cache 2>/dev/null
    end
    printf '  \\033[0;36m[claude-mprj] modelo: %s (cache 7 dias)\\033[0m\\n' $best >&2
    echo $best
end

function update-mprj-model
    rm -f "$HOME/.claude-mprj/.model-cache.json"
    _get_mprj_model > /dev/null
end

# --- Claude Code: funções por conta ------------------------------------------

function claude-mprj
    set extra_args
    set has_model false
    for arg in $argv
        if test "$arg" = "--model"; set has_model true; break; end
    end

    if not $has_model
        set model (_get_mprj_model)
        test -n "$model"; and set extra_args --model $model
    end
    set -lx CLAUDE_CONFIG_DIR ~/.claude-mprj
    set -lx CLAUDE_CODE_USE_FOUNDRY 1
    set -lx ANTHROPIC_FOUNDRY_RESOURCE "gomas-mok8hc25-eastus2"
    set -lx ANTHROPIC_FOUNDRY_API_KEY (cat ~/.secrets/claude-mprj.key 2>/dev/null)
    command claude $extra_args $argv
end

function claude-pro
    set extra_args
    set has_model false
    for arg in $argv
        if test "$arg" = "--model"; set has_model true; break; end
    end

    if not $has_model
        if test -z "$_claude_pro_model"
            set available (_get_anthropic_models)
            set -g _claude_pro_model (_select_best_model "$available" "claude-sonnet-4-6")
            printf '  \\033[0;36m[claude-pro] modelo: %s\\033[0m\\n' $_claude_pro_model
        end
        test -n "$_claude_pro_model"; and set extra_args --model $_claude_pro_model
    end
    set -lx CLAUDE_CONFIG_DIR ~/.claude-pessoal
    command claude $extra_args $argv
end

function claude
    echo 'Use: claude-mprj  ou  claude-pro'
end

abbr --add ch 'claude-pro --model claude-haiku-4-5-20251001'
abbr --add cs 'claude-pro --model claude-sonnet-4-6'
# --- end Claude Code multi-conta ---
"""

# Bloco PowerShell (install.ps1 linhas 275-392)
# Nota: caminho do executável será substituído dinamicamente pela CLI
_POWERSHELL_BLOCK = """
# --- Claude Code: múltiplas contas (v=2) ---

# --- Claude Code: Model Routing -----------------------------------------------
$script:ClaudeSessionCache = @{}

$script:ClaudeModelPriority = @(
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001"
)

function Get-AnthropicModels {
    try {
        $creds = Get-Content "$env:USERPROFILE\\.claude-pessoal\\.credentials.json" -Raw |
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
    $cacheFile = "$env:USERPROFILE\\.claude-mprj\\.model-cache.json"
    if (Test-Path $cacheFile) {
        try {
            $cache = Get-Content $cacheFile -Raw | ConvertFrom-Json
            if (((Get-Date) - [datetime]$cache.cached_at).TotalDays -lt 7) { return $cache.model }
        } catch {}
    }
    Write-Host '[claude-mprj] Detectando modelo disponivel...' -ForegroundColor Yellow
    $best = 'claude-haiku-4-5-20251001'
    foreach ($m in $script:ClaudeModelPriority) {
        & claude --model $m -p '.' --print --output-format json 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $best = $m; break }
    }
    @{ model = $best; cached_at = (Get-Date -Format 'o') } | ConvertTo-Json | Set-Content $cacheFile
    Write-Host "[claude-mprj] modelo: $best (cache 7 dias)" -ForegroundColor Cyan
    return $best
}

function Update-MprjModel {
    Remove-Item "$env:USERPROFILE\\.claude-mprj\\.model-cache.json" -ErrorAction SilentlyContinue
    $env:CLAUDE_CONFIG_DIR = "$env:USERPROFILE\\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY = '1'
    $env:ANTHROPIC_FOUNDRY_RESOURCE = 'gomas-mok8hc25-eastus2'
    try { Get-MprjModel | Out-Null }
    finally {
        Remove-Item Env:\\CLAUDE_CONFIG_DIR, Env:\\CLAUDE_CODE_USE_FOUNDRY,
            Env:\\ANTHROPIC_FOUNDRY_RESOURCE, Env:\\ANTHROPIC_FOUNDRY_API_KEY -ErrorAction SilentlyContinue
    }
}

# --- Claude Code: funções por conta ------------------------------------------

function claude-mprj {
    $env:CLAUDE_CONFIG_DIR          = "$env:USERPROFILE\\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY    = '1'
    $env:ANTHROPIC_FOUNDRY_RESOURCE = 'gomas-mok8hc25-eastus2'
    try {
        $extraArgs = @()
        if ('--model' -notin $args) {
            $model = Get-MprjModel
            if ($model) { $extraArgs = @('--model', $model) }
        }
        & claude @extraArgs @args
    } finally {
        Remove-Item Env:\\CLAUDE_CONFIG_DIR, Env:\\CLAUDE_CODE_USE_FOUNDRY,
            Env:\\ANTHROPIC_FOUNDRY_RESOURCE, Env:\\ANTHROPIC_FOUNDRY_API_KEY -ErrorAction SilentlyContinue
    }
}

function claude-pro {
    $env:CLAUDE_CONFIG_DIR = "$env:USERPROFILE\\.claude-pessoal"
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
        & claude @extraArgs @args
    } finally {
        Remove-Item Env:\\CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
    }
}

function claude { Write-Host "Use: claude-mprj  ou  claude-pro" -ForegroundColor Yellow }

function ch { claude-pro --model claude-haiku-4-5-20251001 @args }
function cs { claude-pro --model claude-sonnet-4-6 @args }
# --- end Claude Code multi-conta ---
"""
