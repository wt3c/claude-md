"""Testes de detecção de plataforma."""
import platform
from pathlib import Path

import pytest

from installer.platform import (
    get_home,
    get_platform,
    get_rc_file,
    get_shell,
    is_linux,
    is_macos,
    is_windows,
)


class TestPlatformDetection:
    """Testes de detecção de plataforma."""

    def test_get_platform_returns_valid_type(self):
        """Retorna tipo de plataforma válido."""
        plat = get_platform()
        assert plat in ["linux", "darwin", "windows"]

    def test_get_home_returns_path(self):
        """Retorna Path do diretório home."""
        home = get_home()
        assert isinstance(home, Path)
        assert home.exists()

    def test_is_linux_on_linux(self, monkeypatch):
        """is_linux() retorna True no Linux."""
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        assert is_linux() is True
        assert is_windows() is False
        assert is_macos() is False

    def test_is_windows_on_windows(self, monkeypatch):
        """is_windows() retorna True no Windows."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        assert is_windows() is True
        assert is_linux() is False
        assert is_macos() is False

    def test_is_macos_on_darwin(self, monkeypatch):
        """is_macos() retorna True no macOS."""
        monkeypatch.setattr(platform, "system", lambda: "Darwin")
        assert is_macos() is True
        assert is_linux() is False
        assert is_windows() is False


class TestShellDetection:
    """Testes de detecção de shell."""

    def test_get_shell_from_env(self, monkeypatch):
        """Detecta shell da variável SHELL."""
        monkeypatch.setenv("SHELL", "/usr/bin/fish")
        assert get_shell() == "fish"

        monkeypatch.setenv("SHELL", "/bin/bash")
        assert get_shell() == "bash"

        monkeypatch.setenv("SHELL", "/usr/bin/zsh")
        assert get_shell() == "zsh"

    def test_get_shell_defaults_to_bash_on_linux(self, monkeypatch):
        """Default para bash no Linux sem SHELL."""
        monkeypatch.delenv("SHELL", raising=False)
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        assert get_shell() == "bash"

    def test_get_shell_returns_powershell_on_windows(self, monkeypatch):
        """Retorna powershell no Windows."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        assert get_shell() == "powershell"


class TestRcFile:
    """Testes de detecção de arquivo rc."""

    def test_get_rc_file_bash(self, temp_home):
        """Retorna ~/.bashrc para bash."""
        rc_file = get_rc_file("bash", temp_home)
        assert rc_file == temp_home / ".bashrc"

    def test_get_rc_file_zsh(self, temp_home):
        """Retorna ~/.zshrc para zsh."""
        rc_file = get_rc_file("zsh", temp_home)
        assert rc_file == temp_home / ".zshrc"

    def test_get_rc_file_fish(self, temp_home):
        """Retorna ~/.config/fish/conf.d/claude.fish para fish."""
        rc_file = get_rc_file("fish", temp_home)
        assert rc_file == temp_home / ".config" / "fish" / "conf.d" / "claude.fish"

    def test_get_rc_file_powershell(self, temp_home):
        """Retorna profile.ps1 para powershell."""
        rc_file = get_rc_file("powershell", temp_home)
        # Windows usa Documents/PowerShell/profile.ps1
        # Mas em temp_home vamos usar .config/powershell/profile.ps1
        assert "profile.ps1" in str(rc_file)
