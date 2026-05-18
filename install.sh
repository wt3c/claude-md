#!/usr/bin/env bash
# install.sh — Claude Code: instalação e configuração global (Linux)
# Uso: bash install.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Cores e helpers ──────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()    { printf "${BLUE}▶${NC}  %s\n" "$*"; }
success() { printf "${GREEN}✔${NC}  %s\n" "$*"; }
warn()    { printf "${YELLOW}⚠${NC}  %s\n" "$*"; }
error()   { printf "${RED}✖${NC}  %s\n" "$*" >&2; exit 1; }
sep()     { printf "\n${BLUE}%s${NC}\n\n" "────────────────────────────────────────────"; }

ask() {
    local _r
    local default="${2:-}"
    local hint="${default:+ [$default]}"
    read -rp "  ${1}${hint}: " _r
    echo "${_r:-$default}"
}

ask_yn() {
    local _r
    local default="${2:-y}"
    local hint; [[ "$default" == "y" ]] && hint="[Y/n]" || hint="[y/N]"
    read -rp "  ${1} ${hint}: " _r
    _r="${_r:-$default}"
    [[ "$_r" =~ ^[Yy]$ ]]
}

# ─── Pré-requisitos ───────────────────────────────────────────────────────────
check_prereqs() {
    sep
    info "Verificando pré-requisitos..."

    command -v git &>/dev/null || error "Git não encontrado."
    success "Git $(git --version | awk '{print $3}')"

    command -v node &>/dev/null \
        || error "Node.js não encontrado. Instale em https://nodejs.org (v18+)"
    local ver; ver=$(node --version | sed 's/v//')
    local major; major=$(echo "$ver" | cut -d. -f1)
    (( major >= 18 )) \
        || error "Node.js v$ver encontrado — requer v18+. Atualize em https://nodejs.org"
    success "Node.js v$ver"

    command -v claude &>/dev/null \
        || error "Claude Code não encontrado. Instale com: npm install -g @anthropic-ai/claude-code"
    success "Claude Code $(claude --version 2>/dev/null | head -1 || echo '(ok)')"
}

# ─── Atualizar repositório ────────────────────────────────────────────────────
update_repo() {
    sep
    info "Atualizando repositório em $REPO_DIR ..."
    if git -C "$REPO_DIR" remote get-url origin &>/dev/null; then
        git -C "$REPO_DIR" pull --ff-only \
            && success "Repositório atualizado" \
            || warn "Pull falhou — continuando com versão local"
    else
        warn "Sem remote configurado — usando versão local"
    fi
}

# ─── Instalar arquivos em um diretório ───────────────────────────────────────
install_to_dir() {
    local target="$1"

    mkdir -p "$target/tasks/archive"

    cp "$REPO_DIR/CLAUDE.md"     "$target/CLAUDE.md"
    cp "$REPO_DIR/settings.json" "$target/settings.json"
    [[ -f "$REPO_DIR/.mcp.json" ]] && cp "$REPO_DIR/.mcp.json" "$target/.mcp.json"
    mkdir -p "$target/skills" "$target/commands"
    cp -r "$REPO_DIR/skills/"*   "$target/skills/"
    cp -r "$REPO_DIR/commands/"* "$target/commands/"

    for f in todo.md lessons.md decisions.md; do
        [[ ! -f "$target/tasks/$f" ]] && cp "$REPO_DIR/tasks/$f" "$target/tasks/$f"
    done

    touch "$target/audit.log"
}

# ─── Configurar funções no shell ──────────────────────────────────────────────
MARKER="# --- Claude Code: múltiplas contas ---"

_append_bash_zsh() {
    local rc="$1"
    grep -q "$MARKER" "$rc" 2>/dev/null && { warn "Funções já presentes em $rc — pulando"; return; }
    # shellcheck disable=SC2016
    cat >> "$rc" <<'SHELLBLOCK'

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

    if command -v python3 &>/dev/null; then
        python3 -c "
import json, sys
from datetime import datetime, timezone
data = {'model': sys.argv[1], 'cached_at': datetime.now(timezone.utc).isoformat()}
with open(sys.argv[2], 'w') as f:
    json.dump(data, f)
" "$best" "$cache" 2>/dev/null
    fi
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

    if ! $has_model; then
        local model; model=$(_get_mprj_model)
        [[ -n "$model" ]] && extra_args=("--model" "$model")
    fi
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
        if [[ -z "$_CLAUDE_PRO_MODEL" ]]; then
            local available; available=$(_get_anthropic_models)
            _CLAUDE_PRO_MODEL=$(_select_best_model "$available" "claude-sonnet-4-6")
            printf '  \033[0;36m[claude-pro] modelo: %s\033[0m\n' "$_CLAUDE_PRO_MODEL"
        fi
        [[ -n "$_CLAUDE_PRO_MODEL" ]] && extra_args=("--model" "$_CLAUDE_PRO_MODEL")
    fi
    CLAUDE_CONFIG_DIR=~/.claude-pessoal \
    command claude "${extra_args[@]}" "$@"
}

alias claude="echo 'Use: claude-mprj  ou  claude-pro'"
alias ch='claude-pro --model claude-haiku-4-5-20251001'
alias cs='claude-pro --model claude-sonnet-4-6'
SHELLBLOCK
    success "Funções adicionadas em $rc"
}

_append_fish() {
    local conf="$HOME/.config/fish/conf.d/claude.fish"
    mkdir -p "$(dirname "$conf")"
    grep -q "$MARKER" "$conf" 2>/dev/null && { warn "Funções já presentes em $conf — pulando"; return; }
    cat > "$conf" <<'FISHBLOCK'
# --- Claude Code: múltiplas contas ---

# --- Claude Code: Model Routing -----------------------------------------------
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
        if test -n "$age"; and test (math "int($age)") -lt 604800
            python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" $cache 2>/dev/null; and return
        end
    end

    printf '  \033[1;33m[claude-mprj] Detectando modelo disponivel...\033[0m\n' >&2
    set best "claude-haiku-4-5-20251001"
    for m in $_claude_model_priority
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
    printf '  \033[0;36m[claude-mprj] modelo: %s (cache 7 dias)\033[0m\n' $best >&2
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
            printf '  \033[0;36m[claude-pro] modelo: %s\033[0m\n' $_claude_pro_model
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
FISHBLOCK
    success "Funções configuradas em $conf"
}

configure_shell() {
    sep
    info "Configurar funções claude-mprj / claude-pro:"
    echo "  1) Bash  (~/.bashrc)"
    echo "  2) Zsh   (~/.zshrc)"
    echo "  3) Fish  (~/.config/fish/conf.d/claude.fish)"
    echo "  4) Todos"
    echo "  5) Pular"
    local choice; choice=$(ask "Escolha [1-5]" "1")
    case "$choice" in
        1) _append_bash_zsh "$HOME/.bashrc" ;;
        2) _append_bash_zsh "$HOME/.zshrc"  ;;
        3) _append_fish ;;
        4) _append_bash_zsh "$HOME/.bashrc"
           _append_bash_zsh "$HOME/.zshrc"
           _append_fish ;;
        *) warn "Configuração de shell pulada — consulte INSTALL.md para configurar manualmente" ;;
    esac
}

# ─── API Key Foundry ──────────────────────────────────────────────────────────
configure_api_key() {
    sep
    info "API Key Foundry (MPRJ) ..."
    local key; key=$(ask "Cole a API Key (sk-ant-...) ou Enter para configurar depois")
    if [[ -n "$key" ]]; then
        mkdir -p "$HOME/.secrets"
        echo "$key" > "$HOME/.secrets/claude-mprj.key"
        chmod 600 "$HOME/.secrets/claude-mprj.key"
        success "Chave salva em ~/.secrets/claude-mprj.key (chmod 600)"
    else
        warn "Chave não configurada. Salve depois em ~/.secrets/claude-mprj.key"
    fi
}

# ─── Token GitLab ─────────────────────────────────────────────────────────────
configure_gitlab() {
    sep
    info "Token GitLab MPRJ ..."
    local token; token=$(ask "Cole o token (glpat-...) ou Enter para configurar depois")
    [[ -z "$token" ]] && { warn "Token GitLab não configurado — configure manualmente no shell"; return; }

    local rc_file=""
    case "${SHELL##*/}" in
        fish) rc_file="$HOME/.config/fish/conf.d/claude.fish" ;;
        zsh)  rc_file="$HOME/.zshrc" ;;
        *)    rc_file="$HOME/.bashrc" ;;
    esac

    # Não duplicar
    grep -q "GITLAB_TOKEN" "$rc_file" 2>/dev/null \
        && { warn "GITLAB_TOKEN já presente em $rc_file — pulando"; return; }

    if [[ "${SHELL##*/}" == "fish" ]]; then
        mkdir -p "$(dirname "$rc_file")"
        printf '\nset -x GITLAB_TOKEN "%s"\nset -x GITLAB_URL "https://gitlab-dti.mprj.mp.br"\n' \
            "$token" >> "$rc_file"
    else
        printf '\nexport GITLAB_TOKEN="%s"\nexport GITLAB_URL="https://gitlab-dti.mprj.mp.br"\n' \
            "$token" >> "$rc_file"
    fi
    success "GITLAB_TOKEN adicionado em $rc_file"
}

# ─── API Key Postman ──────────────────────────────────────────────────────────
configure_postman_key() {
    sep
    info "API Key Postman ..."
    local key; key=$(ask "Cole a API Key do Postman ou Enter para configurar depois")
    [[ -z "$key" ]] && { warn "POSTMAN_API_KEY não configurado — configure manualmente no shell"; return; }

    local rc_file=""
    case "${SHELL##*/}" in
        fish) rc_file="$HOME/.config/fish/conf.d/claude.fish" ;;
        zsh)  rc_file="$HOME/.zshrc" ;;
        *)    rc_file="$HOME/.bashrc" ;;
    esac

    grep -q "POSTMAN_API_KEY" "$rc_file" 2>/dev/null \
        && { warn "POSTMAN_API_KEY já presente em $rc_file — pulando"; return; }

    if [[ "${SHELL##*/}" == "fish" ]]; then
        mkdir -p "$(dirname "$rc_file")"
        printf '\nset -x POSTMAN_API_KEY "%s"\n' "$key" >> "$rc_file"
    else
        printf '\nexport POSTMAN_API_KEY="%s"\n' "$key" >> "$rc_file"
    fi
    success "POSTMAN_API_KEY adicionado em $rc_file"
}

# ─── MCP Servers ──────────────────────────────────────────────────────────────
install_mcps() {
    sep
    info "Instalando MCP servers globais..."
    local existing; existing=$(claude mcp list 2>/dev/null || true)

    if echo "$existing" | grep -q "filesystem"; then
        warn "MCP filesystem já instalado — pulando"
    else
        claude mcp add --scope user filesystem -- npx -y \
            @modelcontextprotocol/server-filesystem "$HOME"
        success "MCP filesystem instalado"
    fi

    if echo "$existing" | grep -q "memory"; then
        warn "MCP memory já instalado — pulando"
    else
        claude mcp add --scope user memory -- npx -y @modelcontextprotocol/server-memory
        success "MCP memory instalado"
    fi

    if echo "$existing" | grep -q "gitlab"; then
        warn "MCP gitlab já instalado — pulando"
    else
        claude mcp add --scope user gitlab -- npx -y @modelcontextprotocol/server-gitlab
        success "MCP gitlab instalado"
    fi

    if echo "$existing" | grep -q "postman"; then
        warn "MCP postman já instalado — pulando"
    else
        claude mcp add --scope user postman -- npx -y @postman/postman-mcp-server
        success "MCP postman instalado"
    fi

    info "MCPs postgres e playwright são por projeto — configure via .mcp.json na raiz do projeto"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    printf "\n${BOLD}${BLUE}╔══════════════════════════════════════════════╗${NC}\n"
    printf "${BOLD}${BLUE}║   Claude Code — Instalação Global (Linux)    ║${NC}\n"
    printf "${BOLD}${BLUE}╚══════════════════════════════════════════════╝${NC}\n"

    check_prereqs
    update_repo

    # Múltiplas contas?
    sep
    local multi_conta=false
    ask_yn "Configurar múltiplas contas (MPRJ + Pessoal)?" "y" && multi_conta=true

    # Instalar diretório principal
    sep
    info "Instalando em ~/.claude ..."
    install_to_dir "$HOME/.claude"
    success "~/.claude configurado"

    if $multi_conta; then
        info "Instalando em ~/.claude-mprj ..."
        install_to_dir "$HOME/.claude-mprj"
        success "~/.claude-mprj configurado"

        info "Instalando em ~/.claude-pessoal ..."
        install_to_dir "$HOME/.claude-pessoal"
        success "~/.claude-pessoal configurado"

        configure_api_key
        configure_shell
        configure_gitlab
    fi

    if ask_yn "Instalar MCP servers globais (filesystem, memory, gitlab, postman)?" "y"; then
        install_mcps
        configure_postman_key
    fi

    # Resumo
    sep
    printf "${GREEN}${BOLD}✔ Instalação concluída!${NC}\n\n"
    if $multi_conta; then
        echo "  Próximos passos:"
        echo "  1. Recarregar shell:    source ~/.bashrc  (ou ~/.zshrc / abrir novo terminal)"
        echo "  2. Autenticar MPRJ:     claude-mprj"
        echo "  3. Autenticar pessoal:  claude-pro  →  /login"
        echo ""
        echo "  Renovar token GitLab:"
        echo "  https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens"
    else
        echo "  Próximos passos:"
        echo "  1. Execute: claude"
    fi
    echo ""
}

main "$@"
