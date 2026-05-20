"""
Detecção de plataforma e helpers multiplataforma.
"""

import platform
import sys
from pathlib import Path
from typing import Literal

PlatformType = Literal["linux", "darwin", "windows"]
ShellType = Literal["bash", "zsh", "fish", "powershell"]


def get_platform() -> PlatformType:
    """
    Detecta sistema operacional.

    Returns:
        "linux" | "darwin" | "windows"

    Raises:
        RuntimeError: Se sistema operacional não suportado
    """
    system = platform.system().lower()

    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    else:
        raise RuntimeError(f"Sistema operacional não suportado: {system}")


def get_home() -> Path:
    """
    Retorna diretório HOME do usuário.

    Returns:
        Path do diretório HOME
    """
    return Path.home()


def get_shell() -> ShellType:
    """
    Detecta shell padrão do usuário.

    Returns:
        "bash" | "zsh" | "fish" | "powershell"
    """
    current_platform = get_platform()

    if current_platform == "windows":
        return "powershell"

    # Linux/macOS: detectar via SHELL env var
    import os

    shell_path = os.environ.get("SHELL", "")

    if "fish" in shell_path:
        return "fish"
    elif "zsh" in shell_path:
        return "zsh"
    else:
        return "bash"  # Default para Linux/macOS


def get_rc_file(shell: ShellType, home: Path) -> Path:
    """
    Retorna path do arquivo rc para o shell especificado.

    Args:
        shell: Tipo de shell
        home: Diretório HOME

    Returns:
        Path do arquivo rc
    """
    rc_files = {
        "bash": home / ".bashrc",
        "zsh": home / ".zshrc",
        "fish": home / ".config" / "fish" / "conf.d" / "claude.fish",
        "powershell": home / "Documents" / "PowerShell" / "profile.ps1",
    }

    return rc_files[shell]


def is_windows() -> bool:
    """Retorna True se estiver rodando no Windows."""
    return get_platform() == "windows"


def is_linux() -> bool:
    """Retorna True se estiver rodando no Linux."""
    return get_platform() == "linux"


def is_macos() -> bool:
    """Retorna True se estiver rodando no macOS."""
    return get_platform() == "darwin"
