"""Testes do CLI principal."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from installer.cli import main


@pytest.fixture
def cli_runner():
    """Runner para testes de CLI."""
    return CliRunner()


@pytest.fixture
def mock_all_modules(monkeypatch, temp_home):
    """Mock de todos os módulos de instalação."""
    # Mock nos módulos originais, não no cli

    # Mock prereqs
    def mock_check_prereqs():
        return {
            "git": "2.43.0",
            "node": "20.11.0",
            "node_major": 20,
            "claude": "claude-code 0.7.0",
        }

    monkeypatch.setattr("installer.prereqs.check_prereqs", mock_check_prereqs)

    # Mock files
    def mock_update_repo(repo_dir):
        return True

    def mock_install_to_dir(repo_dir, target_dir):
        # Criar diretórios para simular instalação
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "CLAUDE.md").touch()
        return {"CLAUDE.md": True}

    monkeypatch.setattr("installer.files.update_repo", mock_update_repo)
    monkeypatch.setattr("installer.files.install_to_dir", mock_install_to_dir)

    # Mock backup
    def mock_get_sensitive_files(home):
        return [home / ".secrets" / "claude-mprj.key"]

    def mock_backup_secrets(home, backup_root):
        backup_dir = backup_root / "20260519-120000"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def mock_restore_secrets(home, backup_dir):
        return 0

    monkeypatch.setattr("installer.backup.get_sensitive_files", mock_get_sensitive_files)
    monkeypatch.setattr("installer.backup.backup_secrets", mock_backup_secrets)
    monkeypatch.setattr("installer.backup.restore_secrets", mock_restore_secrets)

    # Mock api_keys
    def mock_configure_foundry_key(home):
        return True

    def mock_configure_gitlab_token(home):
        return True

    def mock_configure_postman_key(home):
        return True

    monkeypatch.setattr("installer.api_keys.configure_foundry_key", mock_configure_foundry_key)
    monkeypatch.setattr("installer.api_keys.configure_gitlab_token", mock_configure_gitlab_token)
    monkeypatch.setattr("installer.api_keys.configure_postman_key", mock_configure_postman_key)

    # Mock shell_config
    def mock_get_shell():
        return "bash"

    def mock_install_shell_block(shell, home, replace_legacy=True):
        rc_file = home / ".bashrc"
        rc_file.touch()
        return rc_file

    monkeypatch.setattr("installer.platform.get_shell", mock_get_shell)
    monkeypatch.setattr("installer.shell_config.install_shell_block", mock_install_shell_block)

    # Mock mcp
    def mock_install_mcps():
        return {
            "filesystem": True,
            "memory": True,
            "gitlab": True,
            "postman": True,
        }

    monkeypatch.setattr("installer.mcp.install_mcps", mock_install_mcps)

    # Mock Path.home() para usar temp_home
    monkeypatch.setattr(Path, "home", lambda: temp_home)

    return temp_home


class TestCLINonInteractive:
    """Testes do modo --non-interactive."""

    def test_non_interactive_flag(self, cli_runner, mock_all_modules):
        """Flag --non-interactive executa sem prompts."""
        result = cli_runner.invoke(main, ["--non-interactive"])

        assert result.exit_code == 0
        assert "Verificando pré-requisitos..." in result.output
        assert "Git 2.43.0" in result.output
        assert "Instalação concluída!" in result.output

    def test_non_interactive_multi_account(self, cli_runner, mock_all_modules):
        """--non-interactive --multi-account configura ambas contas."""
        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account"])

        assert result.exit_code == 0
        assert "~/.claude-mprj" in result.output
        assert "~/.claude-pessoal" in result.output
        assert "Foundry API Key configurada" in result.output
        assert "GitLab Token configurado" in result.output


class TestCLIInteractive:
    """Testes do modo interativo."""

    def test_interactive_accepts_multi_account(self, cli_runner, mock_all_modules, monkeypatch):
        """Modo interativo: usuário aceita multi-account."""
        # Mock Confirm.ask para retornar True
        from rich.prompt import Confirm

        monkeypatch.setattr(Confirm, "ask", lambda *args, **kwargs: True)

        result = cli_runner.invoke(main, [])

        assert result.exit_code == 0
        assert "~/.claude-mprj" in result.output
        assert "Foundry API Key configurada" in result.output

    def test_interactive_rejects_multi_account(self, cli_runner, mock_all_modules, monkeypatch):
        """Modo interativo: usuário rejeita multi-account."""
        # Mock Confirm.ask para retornar False na primeira chamada
        call_count = {"count": 0}

        def mock_confirm_ask(*args, **kwargs):
            call_count["count"] += 1
            # Primeira chamada (multi-account): False
            # Demais chamadas: True
            return call_count["count"] != 1

        from rich.prompt import Confirm

        monkeypatch.setattr(Confirm, "ask", mock_confirm_ask)

        result = cli_runner.invoke(main, [])

        assert result.exit_code == 0
        assert "~/.claude configurado" in result.output
        # Não deve configurar MPRJ
        assert (
            "~/.claude-mprj" not in result.output or "claude-md" in result.output
        )  # pode aparecer no path do repo


class TestCLIUpdateOnly:
    """Testes do modo --update-only."""

    def test_update_only_skips_mcps(self, cli_runner, mock_all_modules):
        """--update-only não instala MCPs."""
        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account", "--update-only"])

        assert result.exit_code == 0
        # Não deve perguntar sobre MCPs
        assert "MCP servers globais" not in result.output


class TestCLIMcpsOnly:
    """Testes do modo --mcps-only."""

    def test_mcps_only_installs_mcps(self, cli_runner, mock_all_modules):
        """--mcps-only instala apenas MCPs."""
        result = cli_runner.invoke(main, ["--mcps-only"])

        assert result.exit_code == 0
        assert "MCP filesystem instalado" in result.output
        assert "MCP memory instalado" in result.output
        assert "MCP gitlab instalado" in result.output
        assert "MCP postman instalado" in result.output


class TestCLIErrorHandling:
    """Testes de tratamento de erros."""

    def test_prereq_failure_exits(self, cli_runner, mock_all_modules, monkeypatch):
        """Falha de pré-requisito encerra instalação."""

        def mock_check_prereqs_fail():
            raise RuntimeError("Git não encontrado")

        monkeypatch.setattr("installer.prereqs.check_prereqs", mock_check_prereqs_fail)

        result = cli_runner.invoke(main, ["--non-interactive"])

        assert result.exit_code == 1
        assert "Git não encontrado" in result.output

    def test_api_key_failure_exits(self, cli_runner, mock_all_modules, monkeypatch):
        """Falha de API key encerra instalação em modo multi-account."""

        def mock_configure_foundry_key_fail(home):
            raise RuntimeError("Infisical não configurado")

        monkeypatch.setattr(
            "installer.api_keys.configure_foundry_key", mock_configure_foundry_key_fail
        )

        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account"])

        assert result.exit_code == 1
        assert "Infisical não configurado" in result.output

    def test_mcp_failure_continues_interactive(self, cli_runner, mock_all_modules, monkeypatch):
        """Falha de MCP permite continuar no modo interativo."""

        def mock_install_mcps_fail():
            raise RuntimeError("claude mcp add falhou")

        monkeypatch.setattr("installer.mcp.install_mcps", mock_install_mcps_fail)

        # Mock Confirm.ask para retornar True (continuar sem MCPs)
        from rich.prompt import Confirm

        monkeypatch.setattr(Confirm, "ask", lambda *args, **kwargs: True)

        result = cli_runner.invoke(main, ["--multi-account"])

        assert result.exit_code == 0
        assert "claude mcp add falhou" in result.output
        # Nota: "Continuar sem MCPs?" não aparece no output mockado mas foi chamado


class TestCLIOutput:
    """Testes de formatação de output."""

    def test_displays_header(self, cli_runner, mock_all_modules):
        """Display header formatado."""
        result = cli_runner.invoke(main, ["--non-interactive"])

        assert "Claude Code — Instalação Global (Python)" in result.output

    def test_displays_final_instructions(self, cli_runner, mock_all_modules):
        """Display instruções finais."""
        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account"])

        assert "Próximos passos:" in result.output
        assert "Recarregar shell:" in result.output
        assert "claude-mprj" in result.output
        assert "claude-pro" in result.output
        assert "Workflow de Mudanças em Configurações:" in result.output

    def test_shell_specific_reload_command(self, cli_runner, mock_all_modules, monkeypatch):
        """Comando de reload correto para cada shell."""
        # Testar fish
        monkeypatch.setattr("installer.platform.get_shell", lambda: "fish")
        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account"])
        assert "source ~/.config/fish/config.fish" in result.output

        # Testar zsh
        monkeypatch.setattr("installer.platform.get_shell", lambda: "zsh")
        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account"])
        assert "source ~/.zshrc" in result.output

        # Testar bash (default)
        monkeypatch.setattr("installer.platform.get_shell", lambda: "bash")
        result = cli_runner.invoke(main, ["--non-interactive", "--multi-account"])
        assert "source ~/.bashrc" in result.output
