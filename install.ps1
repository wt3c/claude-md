#Requires -Version 5.1
# install.ps1 — Claude Code: instalação e configuração global (Windows)
# Uso: .\install.ps1

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupRoot = "$env:USERPROFILE\.claude-md-backups"
$script:BackupDir = $null   # preenchido por Backup-Secrets

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

# ─── Backup de secrets ───────────────────────────────────────────────────────
function Get-SensitiveFiles {
    @(
        "$env:USERPROFILE\.claude\settings.local.json",
        "$env:USERPROFILE\.claude\.mcp.json",
        "$env:USERPROFILE\.claude-mprj\.credentials.json",
        "$env:USERPROFILE\.claude-mprj\.claude.json",
        "$env:USERPROFILE\.claude-mprj\.model-cache.json",
        "$env:USERPROFILE\.claude-mprj\settings.local.json",
        "$env:USERPROFILE\.claude-mprj\.mcp.json",
        "$env:USERPROFILE\.claude-pessoal\.credentials.json",
        "$env:USERPROFILE\.claude-pessoal\.claude.json",
        "$env:USERPROFILE\.claude-pessoal\.model-cache.json",
        "$env:USERPROFILE\.claude-pessoal\settings.local.json",
        "$env:USERPROFILE\.claude-pessoal\.mcp.json"
    )
}

function Backup-EnvVars {
    param([string]$OutFile)
    $names = @('ANTHROPIC_FOUNDRY_API_KEY', 'GITLAB_TOKEN', 'GITLAB_URL', 'POSTMAN_API_KEY')
    $lines = foreach ($n in $names) {
        $val = [Environment]::GetEnvironmentVariable($n, 'User')
        if ($val) { "$n=$val" }
    }
    if ($lines) { $lines | Set-Content -Path $OutFile -Encoding UTF8 }
}

function Backup-Secrets {
    Write-Sep
    Write-Info "Snapshot de chaves e credenciais (BEFORE install)..."
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $script:BackupDir = Join-Path $BackupRoot $ts
    New-Item -ItemType Directory -Force -Path $script:BackupDir | Out-Null

    $count = 0
    foreach ($f in Get-SensitiveFiles) {
        if (Test-Path $f) {
            $rel = $f.Substring($env:USERPROFILE.Length).TrimStart('\')
            $dest = Join-Path $script:BackupDir $rel
            New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
            Copy-Item -Path $f -Destination $dest -Force
            $count++
        }
    }

    Backup-EnvVars (Join-Path $script:BackupDir 'env.snapshot')

    # Mantém os 10 backups mais recentes
    if (Test-Path $BackupRoot) {
        Get-ChildItem -Path $BackupRoot -Directory |
            Sort-Object LastWriteTime -Descending |
            Select-Object -Skip 10 |
            ForEach-Object { Remove-Item $_.FullName -Recurse -Force }
    }

    Write-Success "$count arquivo(s) sensível(is) preservados em $script:BackupDir"
}

function Restore-Secrets {
    if (-not $script:BackupDir -or -not (Test-Path $script:BackupDir)) { return }
    Write-Sep
    Write-Info "Verificação pós-instalação: restaurando chaves se faltarem..."

    $restored = 0; $kept = 0
    foreach ($f in Get-SensitiveFiles) {
        $rel = $f.Substring($env:USERPROFILE.Length).TrimStart('\')
        $from = Join-Path $script:BackupDir $rel
        if (-not (Test-Path $from)) { continue }
        if (-not (Test-Path $f)) {
            New-Item -ItemType Directory -Force -Path (Split-Path $f -Parent) | Out-Null
            Copy-Item -Path $from -Destination $f -Force
            $restored++
            Write-Success "Restaurado: $f"
        } else {
            $kept++
        }
    }

    if ($restored -eq 0) {
        Write-Success "Nada para restaurar — $kept arquivo(s) sensível(is) preservados intactos"
    } else {
        Write-Success "$restored arquivo(s) restaurado(s) do backup"
    }
    Write-Info "Backup completo permanece em: $script:BackupDir"
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
    Copy-Item "$RepoDir\WORKFLOW_CONFIG.md" "$Target\WORKFLOW_CONFIG.md" -Force

    # .mcp.json: preserva se já existir (pode conter senha postgres real)
    if (Test-Path "$RepoDir\.mcp.json") {
        if (Test-Path "$Target\.mcp.json") {
            Write-Warn "$(Split-Path $Target -Leaf)\.mcp.json já existe — preservando (pode conter secrets)"
        } else {
            Copy-Item "$RepoDir\.mcp.json" "$Target\.mcp.json"
        }
    }

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
# Bump $ProfileBlockVersion ao alterar o conteúdo do here-string $block.
# Versões antigas (com marker legacy) são detectadas e migradas com backup.
$ProfileBlockVersion = "2"
$ProfileMarker       = "# --- Claude Code: múltiplas contas (v=2) ---"
$ProfileMarkerLegacy = "# --- Claude Code: múltiplas contas ---"
$ProfileMarkerEnd    = "# --- end Claude Code multi-conta ---"

function Remove-ProfileBlock {
    param([string]$ProfilePath)
    if (-not (Test-Path $ProfilePath)) { return }

    $lines = Get-Content $ProfilePath
    $startIdx = ($lines | Select-String -Pattern '^# --- Claude Code: múltiplas contas' -SimpleMatch:$false |
        Select-Object -First 1).LineNumber
    if (-not $startIdx) { return }

    # Backup antes de modificar
    $bak = "$ProfilePath.before-update-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $ProfilePath $bak -Force

    $endIdx = ($lines[($startIdx-1)..($lines.Count-1)] | Select-String -Pattern '^# --- end Claude Code' |
        Select-Object -First 1).LineNumber
    if ($endIdx) { $endIdx = $startIdx - 1 + $endIdx } else { $endIdx = $lines.Count }

    $newLines = @()
    if ($startIdx -gt 1) { $newLines += $lines[0..($startIdx-2)] }
    if ($endIdx -lt $lines.Count) { $newLines += $lines[$endIdx..($lines.Count-1)] }
    Set-Content -Path $ProfilePath -Value $newLines -Encoding UTF8
    Write-Info "Bloco antigo removido de $ProfilePath (backup: $bak)"
}

function Set-ProfileFunctions {
    param([string]$ClaudeExe)

    if (-not (Test-Path $PROFILE)) {
        New-Item -ItemType File -Force -Path $PROFILE | Out-Null
    }

    $content = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue

    if ($content -and $content.Contains($ProfileMarker)) {
        Write-Success "Funções PowerShell v$ProfileBlockVersion já presentes no `$PROFILE"
        return
    }

    if ($content -and $content.Contains($ProfileMarkerLegacy)) {
        Write-Warn "Versão antiga das funções claude-mprj/claude-pro no `$PROFILE"
        if (Ask-YesNo "Substituir pela v$ProfileBlockVersion (aplica fixes do repo)?" "y") {
            Remove-ProfileBlock $PROFILE
        } else {
            Write-Warn "Mantendo versão antiga (fixes não serão aplicados)"
            return
        }
    }

    # @'...'@ = raw here-string: nenhum $ expande ao escrever.
    # CLAUDE_EXE_PATH é o único placeholder substituído pelo caminho real.
    $block = @'

# --- Claude Code: múltiplas contas (v=2) ---

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
            if (((Get-Date) - [datetime]$cache.cached_at).TotalDays -lt 7) {
                return $cache.model
            }
        } catch {}
    }

    Write-Host '[claude-mprj] Detectando modelo disponivel...' -ForegroundColor Yellow
    $best = 'claude-haiku-4-5-20251001'
    foreach ($m in $script:ClaudeModelPriority) {
        & 'CLAUDE_EXE_PATH' --model $m -p '.' --print --output-format json 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $best = $m; break }
    }

    @{ model = $best; cached_at = (Get-Date -Format 'o') } |
        ConvertTo-Json | Set-Content $cacheFile
    Write-Host "[claude-mprj] modelo: $best (cache 7 dias)" -ForegroundColor Cyan
    return $best
}

function Update-MprjModel {
    # Força re-detecção do melhor modelo disponível no Azure Foundry.
    # Executar após upgrades no Azure.
    Remove-Item "$env:USERPROFILE\.claude-mprj\.model-cache.json" -ErrorAction SilentlyContinue
    $env:CLAUDE_CONFIG_DIR          = "$env:USERPROFILE\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY    = '1'
    $env:ANTHROPIC_FOUNDRY_RESOURCE = 'gomas-mok8hc25-eastus2'
    try { Get-MprjModel | Out-Null }
    finally {
        Remove-Item Env:\CLAUDE_CONFIG_DIR, Env:\CLAUDE_CODE_USE_FOUNDRY,
            Env:\ANTHROPIC_FOUNDRY_RESOURCE, Env:\ANTHROPIC_FOUNDRY_API_KEY -ErrorAction SilentlyContinue
    }
}

# --- Claude Code: funções por conta ------------------------------------------

function claude-mprj {
    # ANTHROPIC_FOUNDRY_API_KEY deve estar nas variáveis de ambiente do usuário
    $env:CLAUDE_CONFIG_DIR          = "$env:USERPROFILE\.claude-mprj"
    $env:CLAUDE_CODE_USE_FOUNDRY    = '1'
    $env:ANTHROPIC_FOUNDRY_RESOURCE = 'gomas-mok8hc25-eastus2'
    try {
        $extraArgs = @()
        if ('--model' -notin $args) {
            $model = Get-MprjModel
            if ($model) { $extraArgs = @('--model', $model) }
        }
        & 'CLAUDE_EXE_PATH' @extraArgs @args
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
        & 'CLAUDE_EXE_PATH' @extraArgs @args
    } finally {
        Remove-Item Env:\CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
    }
}

function claude {
    Write-Host "Use: claude-mprj  ou  claude-pro" -ForegroundColor Yellow
}

# aliases rapidos: modelo explicito, sempre claude-pro
function ch { claude-pro --model claude-haiku-4-5-20251001 @args }
function cs { claude-pro --model claude-sonnet-4-6 @args }
# --- end Claude Code multi-conta ---
'@
    $escapedExe = $ClaudeExe -replace "'", "''"
    $block = $block.Replace("'CLAUDE_EXE_PATH'", "'$escapedExe'")

    Add-Content -Path $PROFILE -Value $block -Encoding UTF8
    Write-Success "Funções PowerShell v$ProfileBlockVersion instaladas em $PROFILE"
}

# ─── API Key Foundry ──────────────────────────────────────────────────────────
function Set-FoundryApiKey {
    Write-Sep
    Write-Info "API Key Foundry (MPRJ) ..."

    $existing = [Environment]::GetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY", "User")
    if (-not [string]::IsNullOrWhiteSpace($existing)) {
        $masked = "****" + $existing.Substring([Math]::Max(0, $existing.Length - 4))
        Write-Info "Chave existente detectada: $masked"
        if (Ask-YesNo "Manter chave atual?" "y") {
            Write-Success "Chave existente preservada (User env)"
            return
        }
    }

    $key = Read-Host "  Cole a API Key (sk-ant-...) ou Enter para configurar depois"
    if (-not [string]::IsNullOrWhiteSpace($key)) {
        [Environment]::SetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY", $key, "User")
        Write-Success "ANTHROPIC_FOUNDRY_API_KEY salvo nas variáveis de ambiente do usuário"
        Write-Info    "Abra um novo terminal para que a variável fique disponível"
    } elseif (-not [string]::IsNullOrWhiteSpace($existing)) {
        Write-Warn "Entrada vazia — chave antiga MANTIDA"
    } else {
        Write-Warn "Chave não configurada. Configure depois com:"
        Write-Host "  [Environment]::SetEnvironmentVariable('ANTHROPIC_FOUNDRY_API_KEY', 'sk-ant-...', 'User')"
    }
}

# ─── Token GitLab ─────────────────────────────────────────────────────────────
function Set-GitLabToken {
    Write-Sep
    Write-Info "Token GitLab MPRJ ..."

    $existing = [Environment]::GetEnvironmentVariable("GITLAB_TOKEN", "User")
    if (-not [string]::IsNullOrWhiteSpace($existing)) {
        $masked = "****" + $existing.Substring([Math]::Max(0, $existing.Length - 4))
        Write-Info "Token existente detectado: $masked"
        if (Ask-YesNo "Manter token atual?" "y") {
            Write-Success "Token existente preservado (User env)"
            return
        }
    }

    $token = Read-Host "  Cole o token (glpat-...) ou Enter para configurar depois"
    if (-not [string]::IsNullOrWhiteSpace($token)) {
        [Environment]::SetEnvironmentVariable("GITLAB_TOKEN", $token, "User")
        [Environment]::SetEnvironmentVariable("GITLAB_URL", "https://gitlab-dti.mprj.mp.br", "User")
        Write-Success "GITLAB_TOKEN e GITLAB_URL salvos nas variáveis de ambiente do usuário"
        Write-Info    "Abra um novo terminal para que as variáveis fiquem disponíveis"
    } elseif (-not [string]::IsNullOrWhiteSpace($existing)) {
        Write-Warn "Entrada vazia — token antigo MANTIDO"
    } else {
        Write-Warn "Token não configurado. Configure depois em Variáveis de Ambiente do Usuário"
    }
}

# ─── API Key Postman ──────────────────────────────────────────────────────────
function Set-PostmanApiKey {
    Write-Sep
    Write-Info "API Key Postman ..."

    $existing = [Environment]::GetEnvironmentVariable("POSTMAN_API_KEY", "User")
    if (-not [string]::IsNullOrWhiteSpace($existing)) {
        $masked = "****" + $existing.Substring([Math]::Max(0, $existing.Length - 4))
        Write-Info "Chave existente detectada: $masked"
        if (Ask-YesNo "Manter chave atual?" "y") {
            Write-Success "Chave existente preservada (User env)"
            return
        }
    }

    $key = Read-Host "  Cole a API Key do Postman ou Enter para configurar depois"
    if (-not [string]::IsNullOrWhiteSpace($key)) {
        [Environment]::SetEnvironmentVariable("POSTMAN_API_KEY", $key, "User")
        Write-Success "POSTMAN_API_KEY salvo nas variáveis de ambiente do usuário"
        Write-Info    "Abra um novo terminal para que a variável fique disponível"
    } elseif (-not [string]::IsNullOrWhiteSpace($existing)) {
        Write-Warn "Entrada vazia — chave antiga MANTIDA"
    } else {
        Write-Warn "Chave não configurada. Configure depois com:"
        Write-Host "  [Environment]::SetEnvironmentVariable('POSTMAN_API_KEY', 'PMAK-...', 'User')"
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
        @{ Name = "gitlab";     Args = @("npx", "-y", "@modelcontextprotocol/server-gitlab") },
        @{ Name = "postman";    Args = @("npx", "-y", "@postman/postman-mcp-server") }
    )

    foreach ($mcp in $mcps) {
        if ($existing -match $mcp.Name) {
            Write-Warn "MCP $($mcp.Name) já instalado — pulando"
        } else {
            & $ClaudeExe mcp add --scope user $mcp.Name -- @($mcp.Args)
            Write-Success "MCP $($mcp.Name) instalado"
        }
    }

    Write-Info "MCPs postgres e playwright são por projeto — configure via .mcp.json na raiz do projeto"
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
        # .mcp.json / settings.local.json / .credentials.json / .claude.json não são tocados
        Write-Success "Atualizado: $dir (secrets preservados)"
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
    Backup-Secrets

    # Modo: fresh install ou update?
    Write-Sep
    Write-Info "Modo:"
    Write-Host "  1) Instalação completa (primeira vez)"
    Write-Host "  2) Atualizar arquivos existentes (re-instalação)"
    $mode = Ask-Input "Escolha [1/2]" "1"

    if ($mode -eq "2") {
        Update-AllDirs
        Restore-Secrets
        Write-Host ""
        Write-Host "  ✔ Atualização concluída!" -ForegroundColor Green
        if ($script:BackupDir) {
            Write-Host "  Backup de chaves: $script:BackupDir"
        }
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

    if (Ask-YesNo "Instalar MCP servers globais (filesystem, memory, gitlab, postman)?" "y") {
        Install-MCPs $claudeExe
        Set-PostmanApiKey
    }

    # Safety net: restaura qualquer arquivo sensível ausente
    Restore-Secrets

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
    Write-Host "  ⚠ Workflow de Mudanças em Configurações:" -ForegroundColor Yellow
    Write-Host "  Sempre testar mudanças em ~/.claude/ antes de propagar para os ambientes."
    Write-Host "  Veja: WORKFLOW_CONFIG.md ou ~/.claude/WORKFLOW_CONFIG.md"
    Write-Host ""
    if ($script:BackupDir -and (Test-Path $script:BackupDir)) {
        Write-Host "  Backup de chaves/credenciais: $script:BackupDir"
        Write-Host "  (mantidos os 10 backups mais recentes em $BackupRoot)"
        Write-Host ""
    }
}

Main
