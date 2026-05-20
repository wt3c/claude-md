"""
Instalação de arquivos e atualização do repositório.

Equivalente a install_to_dir() e update_repo() do install.sh.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Dict


def install_to_dir(repo_dir: Path, target_dir: Path) -> Dict[str, bool]:
    """
    Instala arquivos do repo em target_dir.

    Equivalente a install_to_dir() do install.sh (linhas 182-210).

    Lógica de sobrescrita:
    - SEMPRE sobrescreve: CLAUDE.md, settings.json, WORKFLOW_CONFIG.md
    - PRESERVA se existir: .mcp.json (pode conter senha postgres customizada)
    - Copia recursivamente: skills/, commands/
    - Copia se não existir: tasks/*.md (todo.md, lessons.md, decisions.md)
    - Sempre cria: audit.log (vazio)

    Args:
        repo_dir: Diretório do repositório
        target_dir: Diretório de destino

    Returns:
        Dict com status de cada operação {filename: bool(copiado)}
        False = preservado/não copiado, True = novo/sobrescrito
    """
    status: Dict[str, bool] = {}

    # Criar estrutura
    (target_dir / "tasks" / "archive").mkdir(parents=True, exist_ok=True)
    (target_dir / "skills").mkdir(parents=True, exist_ok=True)
    (target_dir / "commands").mkdir(parents=True, exist_ok=True)

    # Arquivos sempre sobrescritos
    for filename in ["CLAUDE.md", "settings.json", "WORKFLOW_CONFIG.md"]:
        src = repo_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            status[filename] = True

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
            repo_dir / "skills", target_dir / "skills", dirs_exist_ok=True
        )
        status["skills"] = True

    if (repo_dir / "commands").exists():
        shutil.copytree(
            repo_dir / "commands", target_dir / "commands", dirs_exist_ok=True
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


def update_repo(repo_dir: Path) -> bool:
    """
    Atualiza repositório com git pull --ff-only.

    Equivalente a update_repo() do install.sh (linhas 165-175).

    Args:
        repo_dir: Diretório do repositório

    Returns:
        True se atualizado, False se falhou (não bloqueia instalação)
    """
    try:
        # Verificar se existe remote
        subprocess.run(
            ["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
            capture_output=True,
            check=True,
        )

        # Pull
        subprocess.run(
            ["git", "-C", str(repo_dir), "pull", "--ff-only"],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        # Falhou — continuar com versão local
        return False
