"""Testes de verificação de pré-requisitos."""
import subprocess
from unittest.mock import Mock

import pytest


class TestCheckPrereqs:
    """Testes da função check_prereqs()."""

    def test_detects_git_present(self, mock_commands):
        """Detecta git instalado e retorna versão."""
        from installer.prereqs import check_prereqs

        result = check_prereqs()
        assert result["git"] is not None
        assert isinstance(result["git"], str)

    def test_raises_error_when_git_missing(self, monkeypatch):
        """Levanta RuntimeError quando git ausente."""
        def mock_run(args, *run_args, **kwargs):
            if args[0] == "git":
                raise FileNotFoundError()
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.prereqs import check_prereqs

        with pytest.raises(RuntimeError, match="Git não encontrado"):
            check_prereqs()

    def test_detects_node_version_18_or_higher(self, mock_commands):
        """Aceita Node.js v18+."""
        from installer.prereqs import check_prereqs

        result = check_prereqs()
        assert result["node_major"] >= 18
        assert isinstance(result["node"], str)

    def test_raises_error_when_node_below_18(self, mock_commands):
        """Levanta RuntimeError para Node.js < v18."""
        # Modificar mock para retornar Node v16
        mock_commands["node"].return_value = subprocess.CompletedProcess(
            args=["node", "--version"],
            returncode=0,
            stdout="v16.20.0\n",
            stderr=""
        )

        from installer.prereqs import check_prereqs

        with pytest.raises(RuntimeError, match="Node.js v16.20.0 encontrado — requer v18\\+"):
            check_prereqs()

    def test_raises_error_when_node_missing(self, mock_commands):
        """Levanta RuntimeError quando Node.js ausente."""
        # Configurar mock para levantar FileNotFoundError
        mock_commands["node"].side_effect = FileNotFoundError()

        from installer.prereqs import check_prereqs

        with pytest.raises(RuntimeError, match="Node.js não encontrado"):
            check_prereqs()

    def test_detects_claude_present(self, mock_commands):
        """Detecta Claude Code instalado."""
        from installer.prereqs import check_prereqs

        result = check_prereqs()
        assert result["claude"] is not None
        assert isinstance(result["claude"], str)

    def test_raises_error_when_claude_missing(self, mock_commands):
        """Levanta RuntimeError quando Claude Code ausente."""
        # Configurar mock para levantar FileNotFoundError
        mock_commands["claude"].side_effect = FileNotFoundError()

        from installer.prereqs import check_prereqs

        with pytest.raises(RuntimeError, match="Claude Code não encontrado"):
            check_prereqs()

    def test_returns_all_versions_when_successful(self, mock_commands):
        """Retorna dict completo com todas as versões quando bem-sucedido."""
        from installer.prereqs import check_prereqs

        result = check_prereqs()

        assert "git" in result
        assert "node" in result
        assert "node_major" in result
        assert "claude" in result

        assert result["git"] is not None
        assert result["node"] is not None
        assert result["node_major"] >= 18
        assert result["claude"] is not None
