#Requires -Version 5.1
# install.ps1 — Claude Code: instalação e configuração global (Windows)
# Uso: .\install.ps1

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ─── Helpers ──────────────────────────────────────────────────────────────────
function Write-Info    { param($msg) Write-Host "  `u{25B6}  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "  `u{2714}  $msg" -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host "  `u{26A0}  $msg" -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host "  `u{2716}  $msg" -ForegroundColor Red; exit 1 }

function Write-Sep {
    Write-Host ""
    Write-Host "────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""
}

function Ask-Input {
    param([string]$Prompt, [string]$Default = "")
    $hint = if ($Default) { " [$Default]" } else { "" }
    $val  = Read-Host "  $Prompt$hint"
    if ([string]::IsNullOrWhiteSpace($val)) { $Default } else { $val }
}

function Ask-YesNo {
    param([string]$Prompt, [string]$Default = "y")
    $hint = if ($Default -eq "y") { "[Y/n]" } else { "[y/N]" }
    $val  = Read-Host "  $Prompt $hint"
    if ([string]::IsNullOrWhiteSpace($val)) { $val = $Default }
    return ($val -match '^[Yy]$')
}

# ─── Pré-requisitos ───────────────────────────────────────────────────────────
function Get-ClaudeExe {
    Write-Sep
    Write-Info "Verificando pré-requisitos..."

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Err "Git não encontrado."
    }
    Write-Success "Git $(git --version)"

    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if (-not $nodeCmd) { Write-Err "Node.js não encontrado. Instale em https://nodejs.org (v18+)" }
    $nodeVer = (node --version).TrimStart('v')
    $major   = [int]($nodeVer -split '\.')[0]
    if ($major -lt 18) { Write-Err "Node.js v$nodeVer encontrado — requer v18+. Atualize em https://nodejs.org" }
    Write-Success "Node.js v$nodeVer"

    $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $claudeCmd) {
        Write-Err "Claude Code não encontrado. Instale com: npm install -g @anthropic-ai/claude-code"
    }

    # Guardar o caminho real do executável antes de qualquer função bloqueadora
    $exePath = $claudeCmd.Source
    if ([string]::IsNullOrEmpty($exePath)) {
        $exePath = (Get-Command claude -CommandType Application -ErrorAction SilentlyContinue)?.Source
    }
    Write-Success "Claude Code em: $exePath"

    return $exePath
}

# ─── Atualizar repositório ────────────────────────────────────────────────────
function Update-Repo {
    Write-Sep
    Write-Info "Atualizando repositório em $RepoDir ..."
    Push-Location $RepoDir
    try {
        $remote = git remote get-url origin 2>$null
        if ($remote) {
            git pull --ff-only
            Write-Success "Repositório atualizado"
        } else {
            Write-Warn "Sem remote configurado — usando versão local"
        }
    } catch {
        Write-Warn "Pull falhou — continuando com versão local"
    } finally {
        Pop-Location
    }
}

# ─── Copiar arquivos para um diretório ───────────────────────────────────────
function Install-ToDir {
    param([string]$Target)

    New-Item -ItemType Directory -Force -Path "$Target\tasks\archive" | Out-Null

    Copy-Item "$RepoDir\CLAUDE.md"     "$Target\CLAUDE.md"    -Force
    Copy-Item "$RepoDir\settings.json" "$Target\settings.json" -Force

    New-Item -ItemType Directory -Force -Path "$Target\skills"   | Out-Null
    New-Item -ItemType Directory -Force -Path "$Target\commands" | Out-Null
    Copy-Item "$RepoDir\skills\*"   "$Target\skills\"   -Recurse -Force
    Copy-Item "$RepoDir\commands\*" "$Target\commands\" -Recurse -Force

    foreach ($f in @("todo.md", "lessons.md", "decisions.md")) {
        $dest = "$Target\tasks\$f"
        if (-not (Test-Path $dest)) {
            Copy-Item "$RepoDir\tasks\$f" $dest
        }
    }

    if (-not (Test-Path "$Target\audit.log")) {
        New-Item -ItemType File -Path "$Target\audit.log" | Out-Null
    }
}

# ─── Configurar PowerShell Profile ───────────────────────────────────────────
$ProfileMarker = "# --- Claude Code: múltiplas contas ---"

function Set-ProfileFunctions {
    param([string]$ClaudeExe)

    # Garantir que o profile existe
    if (-not (Test-Path $PROFILE)) {
        New-Item -ItemType File -Force -Path $PROFILE | Out-Null
    }

    $content = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
    if ($content -and $content.Contains($ProfileMarker)) {
        Write-Warn "Funções já presentes no `$PROFILE — pulando"
        return
    }

    $block = @"

$ProfileMarker

# Caminho detectado automaticamente durante a instalação
`$claudeExe = "$ClaudeExe"

function claude-mprj {
    # Autenticação via API Key (Microsoft Foundry)
    # ANTHROPIC_FOUNDRY_API_KEY deve estar nas variáveis de ambiente do usuário
    `$env:CLAUDE_CONFIG_DIR          = "`$env:USERPROFILE\.claude-mprj"
    `$env:CLAUDE_CODE_USE_FOUNDRY    = "1"
    `$env:ANTHROPIC_FOUNDRY_RESOURCE = "gomas-mok8hc25-eastus2"
    & `$claudeExe @args
    Remove-Item Env:\CLAUDE_CONFIG_DIR          -ErrorAction SilentlyContinue
    Remove-Item Env:\CLAUDE_CODE_USE_FOUNDRY    -ErrorAction SilentlyContinue
    Remove-Item Env:\ANTHROPIC_FOUNDRY_RESOURCE -ErrorAction SilentlyContinue
}

function claude-pro {
    # Autenticação OAuth normal — use /login na primeira vez
    `$env:CLAUDE_CONFIG_DIR = "`$env:USERPROFILE\.claude-pessoal"
    & `$claudeExe @args
    Remove-Item Env:\CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
}

function claude {
    Write-Host "Use: claude-mprj  ou  claude-pro" -ForegroundColor Yellow
}
"@

    Add-Content -Path $PROFILE -Value $block -Encoding UTF8
    Write-Success "Funções adicionadas em $PROFILE"
}

# ─── API Key Foundry ──────────────────────────────────────────────────────────
function Set-FoundryApiKey {
    Write-Sep
    Write-Info "API Key Foundry (MPRJ) ..."
    $key = Read-Host "  Cole a API Key (sk-ant-...) ou Enter para configurar depois"
    if (-not [string]::IsNullOrWhiteSpace($key)) {
        [Environment]::SetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY", $key, "User")
        Write-Success "ANTHROPIC_FOUNDRY_API_KEY salvo nas variáveis de ambiente do usuário"
        Write-Info    "Abra um novo terminal para que a variável fique disponível"
    } else {
        Write-Warn "Chave não configurada. Configure depois com:"
        Write-Host "  [Environment]::SetEnvironmentVariable('ANTHROPIC_FOUNDRY_API_KEY', 'sk-ant-...', 'User')"
    }
}

# ─── Token GitLab ─────────────────────────────────────────────────────────────
function Set-GitLabToken {
    Write-Sep
    Write-Info "Token GitLab MPRJ ..."
    $token = Read-Host "  Cole o token (glpat-...) ou Enter para configurar depois"
    if (-not [string]::IsNullOrWhiteSpace($token)) {
        [Environment]::SetEnvironmentVariable("GITLAB_TOKEN", $token, "User")
        [Environment]::SetEnvironmentVariable("GITLAB_URL", "https://gitlab-dti.mprj.mp.br", "User")
        Write-Success "GITLAB_TOKEN e GITLAB_URL salvos nas variáveis de ambiente do usuário"
        Write-Info    "Abra um novo terminal para que as variáveis fiquem disponíveis"
    } else {
        Write-Warn "Token não configurado. Configure depois em Variáveis de Ambiente do Usuário"
    }
}

# ─── MCP Servers ──────────────────────────────────────────────────────────────
function Install-MCPs {
    param([string]$ClaudeExe)
    Write-Sep
    Write-Info "Instalando MCP servers globais..."

    $existing = & $ClaudeExe mcp list 2>$null | Out-String

    $mcps = @(
        @{ Name = "filesystem"; Args = @("npx", "-y", "@modelcontextprotocol/server-filesystem", $env:USERPROFILE) },
        @{ Name = "memory";     Args = @("npx", "-y", "@modelcontextprotocol/server-memory") },
        @{ Name = "gitlab";     Args = @("npx", "-y", "@modelcontextprotocol/server-gitlab") }
    )

    foreach ($mcp in $mcps) {
        if ($existing -match $mcp.Name) {
            Write-Warn "MCP $($mcp.Name) já instalado — pulando"
        } else {
            & $ClaudeExe mcp add --scope global $mcp.Name -- @($mcp.Args)
            Write-Success "MCP $($mcp.Name) instalado"
        }
    }

    Write-Info "MCPs postgres e playwright são por projeto — veja INSTALL.md §6"
}

# ─── Atualizar (sem múltiplas contas) ────────────────────────────────────────
function Update-AllDirs {
    Write-Sep
    Write-Info "Atualizando diretórios de configuração existentes..."
    $dirs = @(".claude", ".claude-mprj", ".claude-pessoal") | ForEach-Object {
        "$env:USERPROFILE\$_"
    } | Where-Object { Test-Path $_ }

    foreach ($dir in $dirs) {
        Copy-Item "$RepoDir\CLAUDE.md"     "$dir\CLAUDE.md"    -Force
        Copy-Item "$RepoDir\settings.json" "$dir\settings.json" -Force
        Copy-Item "$RepoDir\skills\*"   "$dir\skills\"   -Recurse -Force
        Copy-Item "$RepoDir\commands\*" "$dir\commands\" -Recurse -Force
        Write-Success "Atualizado: $dir"
    }
}

# ─── Main ─────────────────────────────────────────────────────────────────────
function Main {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   Claude Code — Instalação Global (Windows)   ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan

    $claudeExe = Get-ClaudeExe
    Update-Repo

    # Modo: fresh install ou update?
    Write-Sep
    Write-Info "Modo:"
    Write-Host "  1) Instalação completa (primeira vez)"
    Write-Host "  2) Atualizar arquivos existentes (re-instalação)"
    $mode = Ask-Input "Escolha [1/2]" "1"

    if ($mode -eq "2") {
        Update-AllDirs
        Write-Host ""
        Write-Host "  ✔ Atualização concluída!" -ForegroundColor Green
        Write-Host ""
        return
    }

    # Múltiplas contas?
    Write-Sep
    $multiConta = Ask-YesNo "Configurar múltiplas contas (MPRJ + Pessoal)?" "y"

    # Instalar diretório principal
    Write-Sep
    Write-Info "Instalando em %USERPROFILE%\.claude ..."
    Install-ToDir "$env:USERPROFILE\.claude"
    Write-Success "%USERPROFILE%\.claude configurado"

    if ($multiConta) {
        Write-Info "Instalando em %USERPROFILE%\.claude-mprj ..."
        Install-ToDir "$env:USERPROFILE\.claude-mprj"
        Write-Success "%USERPROFILE%\.claude-mprj configurado"

        Write-Info "Instalando em %USERPROFILE%\.claude-pessoal ..."
        Install-ToDir "$env:USERPROFILE\.claude-pessoal"
        Write-Success "%USERPROFILE%\.claude-pessoal configurado"

        Set-FoundryApiKey
        Set-GitLabToken

        Write-Sep
        if (Ask-YesNo "Adicionar funções claude-mprj / claude-pro ao PowerShell Profile?" "y") {
            Set-ProfileFunctions $claudeExe
        }
    }

    if (Ask-YesNo "Instalar MCP servers globais (filesystem, memory, gitlab)?" "y") {
        Install-MCPs $claudeExe
    }

    # Resumo
    Write-Sep
    Write-Host "  ✔ Instalação concluída!" -ForegroundColor Green
    Write-Host ""
    if ($multiConta) {
        Write-Host "  Próximos passos:"
        Write-Host "  1. Recarregar o Profile:   . `$PROFILE"
        Write-Host "  2. Autenticar MPRJ:         claude-mprj"
        Write-Host "  3. Autenticar pessoal:      claude-pro  ->  /login"
        Write-Host ""
        Write-Host "  Token GitLab:"
        Write-Host "  https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens"
    } else {
        Write-Host "  Próximos passos:"
        Write-Host "  1. Execute: claude"
    }
    Write-Host ""
}

Main
