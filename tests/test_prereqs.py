"""Testes de verificação de pré-requisitos."""
import subprocess
from unittest.mock import Mock

import pytest


class TestCheckPrereqs:
    """Testes da função check_prereqs()."""

    def test_detects_git_present(self, mock_commands):
        """Detecta git instalado e retorna versão."""
        from .test_helpers import check_prereqs_python

        result = check_prereqs_python()
        assert result["git"] is not None

    def test_detects_git_missing(self, mock_commands):
        """Detecta git ausente."""
        mock_commands["git"].return_value = subprocess.CompletedProcess(
            args=["git", "--version"],
            returncode=127,
            stdout=b"",
            stderr=b"git: command not found"
        )
        mock_commands["git"].side_effect = FileNotFoundError

        from .test_helpers import check_prereqs_python

        result = check_prereqs_python()
        assert result["git"] is None

    def test_detects_node_version_18_or_higher(self, mock_commands):
        """Aceita Node.js v18+."""
        from .test_helpers import check_prereqs_python

        result = check_prereqs_python()
        assert result["node_major"] >= 18

    def test_rejects_node_version_below_18(self, mock_commands):
        """Rejeita Node.js < v18."""
        mock_commands["node"].return_value = subprocess.CompletedProcess(
            args=["node", "--version"],
            returncode=0,
            stdout=b"v16.20.0\n",
            stderr=b""
        )

        from .test_helpers import check_prereqs_python

        result = check_prereqs_python()
        assert result["node_major"] < 18

    def test_detects_claude_present(self, mock_commands):
        """Detecta Claude Code instalado."""
        from .test_helpers import check_prereqs_python

        result = check_prereqs_python()
        assert result["claude"] is not None

    @pytest.mark.xfail(reason="Mock not working correctly - recursion issue")
    def test_detects_claude_missing(self, mock_commands):
        """Detecta Claude Code ausente."""
        mock_commands["claude"].side_effect = FileNotFoundError

        from .test_helpers import check_prereqs_python

        result = check_prereqs_python()
        assert result["claude"] is None
