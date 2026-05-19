"""
Implementações Python das funções dos instaladores para teste.

Estas são implementações de referência que simulam o comportamento
dos scripts Bash/PowerShell para validação dos testes.

IMPORTANTE: Estes helpers serão substituídos pela implementação
real em Python quando a migração for feita.
"""
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List


def get_sensitive_files(home: Path) -> List[Path]:
    """
    Retorna lista de arquivos sensíveis a preservar.

    Equivalente a _sensitive_files() do install.sh.
    """
    return [
        home / ".secrets" / "claude-mprj.key",
        home / ".claude" / "settings.local.json",
        home / ".claude" / ".mcp.json",
        home / ".claude-mprj" / ".credentials.json",
        home / ".claude-mprj" / ".claude.json",
        home / ".claude-mprj" / ".model-cache.json",
        home / ".claude-mprj" / "settings.local.json",
        home / ".claude-mprj" / ".mcp.json",
        home / ".claude-pessoal" / ".credentials.json",
        home / ".claude-pessoal" / ".claude.json",
        home / ".claude-pessoal" / ".model-cache.json",
        home / ".claude-pessoal" / "settings.local.json",
        home / ".claude-pessoal" / ".mcp.json",
    ]


def snapshot_env_vars(home: Path, output_file: Path) -> None:
    """
    Extrai variáveis de ambiente relevantes dos arquivos rc.

    Equivalente a _snapshot_env_vars() do install.sh.
    """
    rc_files = [
        home / ".bashrc",
        home / ".zshrc",
        home / ".config" / "fish" / "conf.d" / "claude.fish",
    ]

    env_vars = [
        "GITLAB_TOKEN",
        "GITLAB_URL",
        "POSTMAN_API_KEY",
        "ANTHROPIC_FOUNDRY_API_KEY",
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w") as out:
        for rc in rc_files:
            if not rc.exists():
                continue

            out.write(f"### {rc}\n")
            content = rc.read_text()

            for var in env_vars:
                # Bash/Zsh: export VAR="value"
                # Fish: set -x VAR "value"
                for pattern in [
                    rf'export {var}="([^"]+)"',
                    rf"export {var}='([^']+)'",
                    rf'set -x {var} "([^"]+)"',
                    rf"set -x {var} '([^']+)'",
                ]:
                    match = re.search(pattern, content)
                    if match:
                        out.write(f'{var}="{match.group(1)}"\n')
                        break

            out.write("\n")


def backup_secrets_python(home: Path, backup_root: Path) -> Path:
    """
    Implementação Python de backup_secrets().

    Args:
        home: Diretório HOME
        backup_root: Diretório raiz para backups

    Returns:
        Path do backup criado
    """
    # Criar timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = backup_root / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.chmod(0o700)

    # Copiar arquivos sensíveis
    for src in get_sensitive_files(home):
        if not src.exists():
            continue

        # Preservar estrutura relativa
        rel_path = src.relative_to(home)
        dest = backup_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dest)

    # Snapshot de env vars
    snapshot_env_vars(home, backup_dir / "env.snapshot")

    # Limpar backups antigos (manter 10)
    if backup_root.exists():
        backups = sorted(backup_root.iterdir(), key=lambda p: p.name, reverse=True)
        for old_backup in backups[10:]:
            shutil.rmtree(old_backup)

    return backup_dir


def restore_secrets_python(home: Path, backup_dir: Path) -> int:
    """
    Implementação Python de restore_secrets().

    Args:
        home: Diretório HOME
        backup_dir: Diretório de backup a restaurar

    Returns:
        Número de arquivos restaurados
    """
    if not backup_dir or not backup_dir.exists():
        return 0

    restored = 0

    for target_file in get_sensitive_files(home):
        rel_path = target_file.relative_to(home)
        source_file = backup_dir / rel_path

        if not source_file.exists():
            continue

        if target_file.exists():
            # Não sobrescrever
            continue

        # Criar diretório pai
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Copiar
        shutil.copy2(source_file, target_file)
        restored += 1

    return restored


def check_prereqs_python() -> dict[str, str]:
    """
    Verifica pré-requisitos (git, node, claude).

    Returns:
        Dict com versões detectadas ou erro
    """
    import subprocess

    result = {}

    # Git
    try:
        proc = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True
        )
        output = proc.stdout.decode() if isinstance(proc.stdout, bytes) else proc.stdout
        parts = output.strip().split()
        result["git"] = parts[-1] if parts else None
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        result["git"] = None

    # Node
    try:
        proc = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            check=True
        )
        output = proc.stdout.decode() if isinstance(proc.stdout, bytes) else proc.stdout
        version = output.strip().lstrip('v')
        major = int(version.split('.')[0])

        result["node"] = version
        result["node_major"] = major
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError, IndexError):
        result["node"] = None
        result["node_major"] = 0

    # Claude
    try:
        proc = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            check=True
        )
        output = proc.stdout.decode() if isinstance(proc.stdout, bytes) else proc.stdout
        result["claude"] = output.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        result["claude"] = None

    return result


def install_to_dir_python(repo_dir: Path, target_dir: Path) -> dict[str, bool]:
    """
    Instala arquivos do repo em um diretório target.

    Args:
        repo_dir: Diretório do repositório
        target_dir: Diretório de destino

    Returns:
        Dict com status de cada operação
    """
    status = {}

    # Criar estrutura
    (target_dir / "tasks" / "archive").mkdir(parents=True, exist_ok=True)
    (target_dir / "skills").mkdir(parents=True, exist_ok=True)
    (target_dir / "commands").mkdir(parents=True, exist_ok=True)

    # Copiar arquivos sempre sobrescritos
    shutil.copy2(repo_dir / "CLAUDE.md", target_dir / "CLAUDE.md")
    status["CLAUDE.md"] = True

    shutil.copy2(repo_dir / "settings.json", target_dir / "settings.json")
    status["settings.json"] = True

    # .mcp.json: preservar se existir
    mcp_source = repo_dir / ".mcp.json"
    mcp_target = target_dir / ".mcp.json"
    if mcp_source.exists():
        if mcp_target.exists():
            status[".mcp.json"] = False  # preservado
        else:
            shutil.copy2(mcp_source, mcp_target)
            status[".mcp.json"] = True

    # Copiar skills e commands
    if (repo_dir / "skills").exists():
        shutil.copytree(
            repo_dir / "skills",
            target_dir / "skills",
            dirs_exist_ok=True
        )
        status["skills"] = True

    if (repo_dir / "commands").exists():
        shutil.copytree(
            repo_dir / "commands",
            target_dir / "commands",
            dirs_exist_ok=True
        )
        status["commands"] = True

    # Copiar tasks apenas se não existirem
    for task_file in ["todo.md", "lessons.md", "decisions.md"]:
        source = repo_dir / "tasks" / task_file
        target = target_dir / "tasks" / task_file

        if source.exists() and not target.exists():
            shutil.copy2(source, target)
            status[f"tasks/{task_file}"] = True
        else:
            status[f"tasks/{task_file}"] = False

    # Criar audit.log
    (target_dir / "audit.log").touch()
    status["audit.log"] = True

    return status


def detect_shell_block_version(rc_file: Path) -> str | None:
    """
    Detecta versão do bloco shell ou None se não existir.

    Returns:
        "v2" | "v1" | None
    """
    if not rc_file.exists():
        return None

    content = rc_file.read_text()

    if "# --- Claude Code: múltiplas contas (v=2) ---" in content:
        return "v2"

    if re.search(r"^# --- Claude Code: múltiplas contas", content, re.MULTILINE):
        return "v1"

    return None


def remove_shell_block(rc_file: Path) -> Path:
    """
    Remove bloco shell e cria backup.

    Returns:
        Path do arquivo de backup
    """
    if not rc_file.exists():
        return None

    # Backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = rc_file.parent / f"{rc_file.name}.before-update-{timestamp}"
    shutil.copy2(rc_file, backup)

    # Remover bloco
    lines = rc_file.read_text().splitlines()
    new_lines = []
    in_block = False

    for line in lines:
        if re.match(r"^# --- Claude Code: múltiplas contas", line):
            in_block = True
            continue
        if in_block and line.startswith("# --- end Claude Code"):
            in_block = False
            continue
        if not in_block:
            new_lines.append(line)

    rc_file.write_text("\n".join(new_lines) + "\n")

    return backup
