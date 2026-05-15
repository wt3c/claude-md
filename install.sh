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
    local use_symlinks="${2:-false}"

    mkdir -p "$target/tasks/archive"

    if [[ "$use_symlinks" == "true" ]]; then
        ln -sf "$REPO_DIR/CLAUDE.md"     "$target/CLAUDE.md"
        ln -sf "$REPO_DIR/settings.json" "$target/settings.json"
        # Diretórios: remover entrada anterior antes de criar o symlink
        rm -rf "${target:?}/skills" "${target:?}/commands"
        ln -s  "$REPO_DIR/skills"    "$target/skills"
        ln -s  "$REPO_DIR/commands"  "$target/commands"
    else
        cp "$REPO_DIR/CLAUDE.md"     "$target/CLAUDE.md"
        cp "$REPO_DIR/settings.json" "$target/settings.json"
        mkdir -p "$target/skills" "$target/commands"
        cp -r "$REPO_DIR/skills/"*   "$target/skills/"
        cp -r "$REPO_DIR/commands/"* "$target/commands/"
    fi

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

function claude-mprj() {
    CLAUDE_CONFIG_DIR=~/.claude-mprj \
    CLAUDE_CODE_USE_FOUNDRY=1 \
    ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
    ANTHROPIC_FOUNDRY_API_KEY="$(cat ~/.secrets/claude-mprj.key 2>/dev/null)" \
    command claude "$@"
}

function claude-pro() {
    CLAUDE_CONFIG_DIR=~/.claude-pessoal \
    command claude "$@"
}

alias claude="echo 'Use: claude-mprj  ou  claude-pro'"
SHELLBLOCK
    success "Funções adicionadas em $rc"
}

_append_fish() {
    local conf="$HOME/.config/fish/conf.d/claude.fish"
    mkdir -p "$(dirname "$conf")"
    grep -q "$MARKER" "$conf" 2>/dev/null && { warn "Funções já presentes em $conf — pulando"; return; }
    cat > "$conf" <<'FISHBLOCK'
# --- Claude Code: múltiplas contas ---

function claude-mprj
    env CLAUDE_CONFIG_DIR=~/.claude-mprj \
        CLAUDE_CODE_USE_FOUNDRY=1 \
        ANTHROPIC_FOUNDRY_RESOURCE="gomas-mok8hc25-eastus2" \
        ANTHROPIC_FOUNDRY_API_KEY=(cat ~/.secrets/claude-mprj.key 2>/dev/null) \
        command claude $argv
end

function claude-pro
    env CLAUDE_CONFIG_DIR=~/.claude-pessoal \
        command claude $argv
end

function claude
    echo 'Use: claude-mprj  ou  claude-pro'
end
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

# ─── MCP Servers ──────────────────────────────────────────────────────────────
install_mcps() {
    sep
    info "Instalando MCP servers globais..."
    local existing; existing=$(claude mcp list 2>/dev/null || true)

    if echo "$existing" | grep -q "filesystem"; then
        warn "MCP filesystem já instalado — pulando"
    else
        claude mcp add --scope global filesystem -- npx -y \
            @modelcontextprotocol/server-filesystem "$HOME"
        success "MCP filesystem instalado"
    fi

    if echo "$existing" | grep -q "memory"; then
        warn "MCP memory já instalado — pulando"
    else
        claude mcp add --scope global memory -- npx -y @modelcontextprotocol/server-memory
        success "MCP memory instalado"
    fi

    if echo "$existing" | grep -q "gitlab"; then
        warn "MCP gitlab já instalado — pulando"
    else
        claude mcp add --scope global gitlab -- npx -y @modelcontextprotocol/server-gitlab
        success "MCP gitlab instalado"
    fi

    info "MCPs postgres e playwright são por projeto — veja INSTALL.md §6"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    printf "\n${BOLD}${BLUE}╔══════════════════════════════════════════════╗${NC}\n"
    printf "${BOLD}${BLUE}║   Claude Code — Instalação Global (Linux)    ║${NC}\n"
    printf "${BOLD}${BLUE}╚══════════════════════════════════════════════╝${NC}\n"

    check_prereqs
    update_repo

    # Tipo de instalação
    sep
    info "Tipo de instalação:"
    echo "  1) Symlinks (recomendado) — git pull reflete automaticamente em ~/.claude/"
    echo "  2) Cópia — independente do repositório (exige re-executar para atualizar)"
    local install_type; install_type=$(ask "Escolha [1/2]" "1")
    local use_symlinks="false"
    [[ "$install_type" == "1" ]] && use_symlinks="true"

    # Múltiplas contas?
    sep
    local multi_conta=false
    ask_yn "Configurar múltiplas contas (MPRJ + Pessoal)?" "y" && multi_conta=true

    # Instalar diretório principal
    sep
    info "Instalando em ~/.claude ..."
    install_to_dir "$HOME/.claude" "$use_symlinks"
    success "~/.claude configurado"

    if $multi_conta; then
        info "Instalando em ~/.claude-mprj ..."
        install_to_dir "$HOME/.claude-mprj" "$use_symlinks"
        success "~/.claude-mprj configurado"

        info "Instalando em ~/.claude-pessoal ..."
        install_to_dir "$HOME/.claude-pessoal" "$use_symlinks"
        success "~/.claude-pessoal configurado"

        configure_api_key
        configure_shell
        configure_gitlab
    fi

    if ask_yn "Instalar MCP servers globais (filesystem, memory, gitlab)?" "y"; then
        install_mcps
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
