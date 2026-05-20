"""Testes de instalação de MCP servers."""
import subprocess

import pytest


class TestGetInstalledMcps:
    """Testes da função get_installed_mcps()."""

    def test_parses_claude_mcp_list_output(self, monkeypatch):
        """Parse output de `claude mcp list`."""
        # Mock output típico de `claude mcp list`
        mock_output = """filesystem: npx @modelcontextprotocol/server-filesystem /home/user - ✓ Connected
memory: npx @modelcontextprotocol/server-memory - ✓ Connected
"""

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp" and args[2] == "list":
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout=mock_output, stderr=""
                )
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import get_installed_mcps

        result = get_installed_mcps()
        assert "filesystem" in result
        assert "memory" in result

    def test_returns_empty_list_when_no_mcps_installed(self, monkeypatch):
        """Retorna lista vazia quando nenhum MCP instalado."""

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp" and args[2] == "list":
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout="", stderr=""
                )
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import get_installed_mcps

        result = get_installed_mcps()
        assert result == []

    def test_handles_claude_mcp_list_error(self, monkeypatch):
        """Retorna lista vazia quando `claude mcp list` falha."""

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp" and args[2] == "list":
                raise subprocess.CalledProcessError(1, args)
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import get_installed_mcps

        result = get_installed_mcps()
        assert result == []


class TestInstallMcps:
    """Testes da função install_mcps()."""

    def test_installs_all_mcps_when_none_exist(self, monkeypatch):
        """Instala todos os 4 MCPs quando nenhum existe."""
        mcp_add_calls = []

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp":
                if args[2] == "list":
                    # Nenhum MCP instalado
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout="", stderr=""
                    )
                elif args[2] == "add":
                    # Registrar chamada
                    mcp_add_calls.append(args)
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout="Added MCP\n", stderr=""
                    )
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import install_mcps

        result = install_mcps()

        # Todos os 4 MCPs devem ter sido instalados
        assert result["filesystem"] is True
        assert result["memory"] is True
        assert result["gitlab"] is True
        assert result["postman"] is True

        # Verificar que foram feitas 4 chamadas de `claude mcp add`
        assert len(mcp_add_calls) == 4

    def test_skips_already_installed_mcps(self, monkeypatch):
        """Pula MCPs já instalados."""
        mcp_add_calls = []

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp":
                if args[2] == "list":
                    # filesystem e memory já instalados
                    return subprocess.CompletedProcess(
                        args=args,
                        returncode=0,
                        stdout="filesystem: npx ...\nmemory: npx ...\n",
                        stderr="",
                    )
                elif args[2] == "add":
                    mcp_add_calls.append(args)
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout="Added MCP\n", stderr=""
                    )
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import install_mcps

        result = install_mcps()

        # filesystem e memory já existem (False = pulado)
        assert result["filesystem"] is False
        assert result["memory"] is False

        # gitlab e postman instalados agora (True = novo)
        assert result["gitlab"] is True
        assert result["postman"] is True

        # Apenas 2 chamadas de `claude mcp add` (gitlab e postman)
        assert len(mcp_add_calls) == 2

    def test_raises_error_when_mcp_add_fails(self, monkeypatch):
        """Levanta RuntimeError quando `claude mcp add` falha."""

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp":
                if args[2] == "list":
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout="", stderr=""
                    )
                elif args[2] == "add":
                    # Simular falha
                    raise subprocess.CalledProcessError(
                        1, args, stderr="Error: failed to install"
                    )
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import install_mcps

        with pytest.raises(RuntimeError, match="Falha ao instalar MCP"):
            install_mcps()

    def test_replaces_home_variable_in_args(self, monkeypatch):
        """Substitui $HOME pelo path real nos argumentos."""
        import os

        mcp_add_calls = []

        def mock_run(args, *run_args, **kwargs):
            if args[0] == "claude" and args[1] == "mcp":
                if args[2] == "list":
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout="", stderr=""
                    )
                elif args[2] == "add":
                    mcp_add_calls.append(args)
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout="Added MCP\n", stderr=""
                    )
            return subprocess.run(args, *run_args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_run)

        from installer.mcp import install_mcps

        install_mcps()

        # Encontrar a chamada do filesystem MCP
        filesystem_call = [c for c in mcp_add_calls if "filesystem" in c][0]

        # Verificar que $HOME foi substituído pelo path real
        home_path = os.path.expanduser("~")
        assert home_path in filesystem_call
        assert "$HOME" not in filesystem_call
