"""
Backup e restore de secrets.

Equivalente a backup_secrets() e restore_secrets() do install.sh (linhas 83-141).
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from installer.platform import is_windows


def get_sensitive_files(home: Path) -> List[Path]:
    """
    Retorna lista de arquivos sensíveis a preservar.

    Equivalente a _sensitive_files() do install.sh (linhas 38-53).

    Args:
        home: Diretório HOME

    Returns:
        Lista de 13 arquivos sensíveis (Linux) ou 12 (Windows)
    """
    files = [
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

    # Linux: adicionar chave Foundry (Windows usa variável de ambiente)
    if not is_windows():
        files.append(home / ".secrets" / "claude-mprj.key")

    return files


def snapshot_env_vars(home: Path, output_file: Path) -> None:
    """
    Extrai variáveis de ambiente relevantes dos arquivos rc.

    Equivalente a _snapshot_env_vars() do install.sh (linhas 66-81).

    Args:
        home: Diretório HOME
        output_file: Arquivo de saída para snapshot
    """
    if is_windows():
        # Windows: lê de variáveis de ambiente User
        import os

        env_vars = [
            "ANTHROPIC_FOUNDRY_API_KEY",
            "GITLAB_TOKEN",
            "GITLAB_URL",
            "POSTMAN_API_KEY",
        ]

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w") as out:
            out.write("### Windows User Environment Variables\n")
            for var in env_vars:
                value = os.environ.get(var)
                if value:
                    out.write(f'{var}="{value}"\n')
            out.write("\n")
    else:
        # Linux: lê de rc files
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


def backup_secrets(home: Path, backup_root: Path) -> Path:
    """
    Cria backup timestamped de secrets + snapshot env vars + limpa antigos (mantém 10).

    Equivalente a backup_secrets() do install.sh (linhas 83-112).

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


def restore_secrets(home: Path, backup_dir: Path) -> int:
    """
    Restaura arquivos sensíveis ausentes (NÃO sobrescreve existentes).

    Equivalente a restore_secrets() do install.sh (linhas 115-141).

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
