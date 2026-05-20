"""
Testes para o módulo de desinstalação.
"""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from installer.platform import is_windows
from installer.uninstall import (
    get_paths_to_remove,
    get_shell_files_to_clean,
    remove_paths,
)


def test_get_paths_to_remove_linux(tmp_path: Path, monkeypatch):
    """Testa get_paths_to_remove no Linux."""
    monkeypatch.setattr("installer.uninstall.is_windows", lambda: False)

    paths = get_paths_to_remove(tmp_path)

    assert len(paths) == 4
    assert any(str(p).endswith(".claude-pessoal") for p, _ in paths)
    assert any(str(p).endswith(".claude-mprj") for p, _ in paths)
    assert any(str(p).endswith(".claude") for p, _ in paths)
    assert any(str(p).endswith("claude-mprj.key") for p, _ in paths)


def test_get_paths_to_remove_windows(tmp_path: Path, monkeypatch):
    """Testa get_paths_to_remove no Windows."""
    monkeypatch.setattr("installer.uninstall.is_windows", lambda: True)

    paths = get_paths_to_remove(tmp_path)

    assert len(paths) == 3
    assert any(str(p).endswith(".claude-pessoal") for p, _ in paths)
    assert any(str(p).endswith(".claude-mprj") for p, _ in paths)
    assert any(str(p).endswith(".claude") for p, _ in paths)
    assert not any("claude-mprj.key" in str(p) for p, _ in paths)


def test_get_shell_files_to_clean_linux(tmp_path: Path, monkeypatch):
    """Testa get_shell_files_to_clean no Linux."""
    monkeypatch.setattr("installer.uninstall.is_windows", lambda: False)

    files = get_shell_files_to_clean(tmp_path)

    assert len(files) == 3
    assert any(str(p).endswith(".bashrc") for p, _ in files)
    assert any(str(p).endswith(".zshrc") for p, _ in files)
    assert any(str(p).endswith("claude.fish") for p, _ in files)


def test_get_shell_files_to_clean_windows(tmp_path: Path, monkeypatch):
    """Testa get_shell_files_to_clean no Windows."""
    monkeypatch.setattr("installer.uninstall.is_windows", lambda: True)

    files = get_shell_files_to_clean(tmp_path)

    assert len(files) == 2
    assert any("PowerShell" in str(p) for p, _ in files)
    assert any("Microsoft.PowerShell_profile.ps1" in str(p) for p, _ in files)


def test_remove_paths_directories(tmp_path: Path):
    """Testa remoção de diretórios."""
    # Criar estrutura
    dir1 = tmp_path / ".claude-pessoal"
    dir2 = tmp_path / ".claude-mprj"
    dir3 = tmp_path / ".claude"

    dir1.mkdir()
    dir2.mkdir()
    dir3.mkdir()

    # Criar arquivos dentro
    (dir1 / "test.txt").write_text("test")
    (dir2 / "test.txt").write_text("test")
    (dir3 / "test.txt").write_text("test")

    # Remover
    remove_paths([dir1, dir2, dir3])

    # Verificar
    assert not dir1.exists()
    assert not dir2.exists()
    assert not dir3.exists()


def test_remove_paths_files(tmp_path: Path):
    """Testa remoção de arquivos."""
    # Criar arquivos
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("test")
    file2.write_text("test")

    # Remover
    remove_paths([file1, file2])

    # Verificar
    assert not file1.exists()
    assert not file2.exists()


def test_remove_paths_nonexistent(tmp_path: Path):
    """Testa remoção de paths inexistentes (não deve falhar)."""
    file1 = tmp_path / "nonexistent.txt"

    # Não deve lançar exceção
    remove_paths([file1])

    assert not file1.exists()


def test_remove_paths_mixed(tmp_path: Path):
    """Testa remoção mista (diretórios + arquivos + inexistentes)."""
    dir1 = tmp_path / "dir1"
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "nonexistent.txt"

    dir1.mkdir()
    (dir1 / "nested.txt").write_text("test")
    file1.write_text("test")

    remove_paths([dir1, file1, file2])

    assert not dir1.exists()
    assert not file1.exists()
    assert not file2.exists()


def test_preview_removal_integration(tmp_path: Path, monkeypatch, capsys):
    """Testa preview_removal com estrutura real."""
    monkeypatch.setattr("installer.uninstall.is_windows", lambda: False)
    monkeypatch.setattr("installer.uninstall.get_home", lambda: tmp_path)

    # Criar estrutura
    (tmp_path / ".claude-pessoal").mkdir()
    (tmp_path / ".claude-mprj").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".bashrc").write_text("test")

    # Importar função aqui para pegar o monkeypatch
    from installer.uninstall import preview_removal

    paths, shell_files, size = preview_removal(tmp_path)

    assert len(paths) == 3  # Diretórios criados
    assert len(shell_files) == 1  # .bashrc existe

    # Verificar output
    captured = capsys.readouterr()
    assert "PREVIEW DE DESINSTALAÇÃO" in captured.out
    assert ".claude-pessoal" in captured.out
    assert ".bashrc" in captured.out


def test_confirm_removal_yes(monkeypatch):
    """Testa confirmação com resposta positiva."""
    monkeypatch.setattr("builtins.input", lambda: "s")

    from installer.uninstall import confirm_removal

    assert confirm_removal() is True


def test_confirm_removal_no(monkeypatch):
    """Testa confirmação com resposta negativa."""
    monkeypatch.setattr("builtins.input", lambda: "n")

    from installer.uninstall import confirm_removal

    assert confirm_removal() is False


def test_confirm_removal_variants(monkeypatch):
    """Testa diferentes variantes de confirmação."""
    from installer.uninstall import confirm_removal

    # Positivas
    for response in ["s", "S", "sim", "SIM", "y", "Y", "yes", "YES"]:
        monkeypatch.setattr("builtins.input", lambda r=response: r)
        assert confirm_removal() is True

    # Negativas
    for response in ["n", "N", "nao", "NAO", "no", "NO", "", "invalid"]:
        monkeypatch.setattr("builtins.input", lambda r=response: r)
        assert confirm_removal() is False
