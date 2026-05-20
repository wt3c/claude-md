"""
Verificação de pré-requisitos (git, node v18+, claude).

Equivalente a check_prereqs() do install.sh (linhas 144-162).
"""

import subprocess
from typing import Dict, Optional


def check_prereqs() -> Dict[str, Optional[str]]:
    """
    Verifica pré-requisitos: git, node (v18+), claude.

    Returns:
        Dict com versões detectadas:
        {
            "git": "2.43.0" | None,
            "node": "20.11.0" | None,
            "node_major": 20 | 0,
            "claude": "claude-code 0.7.0" | None,
        }

    Raises:
        RuntimeError: Se qualquer pré-requisito falhar
    """
    result: Dict[str, Optional[str | int]] = {}

    # Git
    try:
        proc = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
            text=True,
        )
        parts = proc.stdout.strip().split()
        result["git"] = parts[-1] if parts else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("Git não encontrado. Instale em https://git-scm.com")

    # Node
    try:
        proc = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            check=True,
            text=True,
        )
        version = proc.stdout.strip().lstrip("v")
        major = int(version.split(".")[0])

        result["node"] = version
        result["node_major"] = major

        if major < 18:
            raise RuntimeError(
                f"Node.js v{version} encontrado — requer v18+. "
                "Atualize em https://nodejs.org"
            )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("Node.js não encontrado. Instale em https://nodejs.org (v18+)")
    except (ValueError, IndexError):
        raise RuntimeError("Não foi possível parsear versão do Node.js")

    # Claude
    try:
        proc = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            check=True,
            text=True,
        )
        result["claude"] = proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "Claude Code não encontrado. Instale com: "
            "npm install -g @anthropic-ai/claude-code"
        )

    return result  # type: ignore[return-value]
