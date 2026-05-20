"""Testes de instalação de arquivos."""
from pathlib import Path

import pytest

from .conftest import assert_dir_exists, assert_file_exists


class TestInstallToDir:
    """Testes da função install_to_dir()."""

    def test_creates_directory_structure(self, mock_repo, tmp_path):
        """Cria estrutura completa de diretórios."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        install_to_dir(mock_repo, target)

        assert_dir_exists(target)
        assert_dir_exists(target / "tasks" / "archive")
        assert_dir_exists(target / "skills")
        assert_dir_exists(target / "commands")

    def test_copies_always_overwritten_files(self, mock_repo, tmp_path):
        """Copia CLAUDE.md e settings.json sempre (sobrescreve)."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        target.mkdir()

        # Criar arquivos existentes com conteúdo diferente
        (target / "CLAUDE.md").write_text("# OLD VERSION\n")
        (target / "settings.json").write_text('{"old": true}\n')

        status = install_to_dir(mock_repo, target)

        assert status["CLAUDE.md"] is True
        assert status["settings.json"] is True

        # Verificar que foram sobrescritos
        assert "OLD VERSION" not in (target / "CLAUDE.md").read_text()
        assert '"old": true' not in (target / "settings.json").read_text()

    def test_preserves_mcp_json_if_exists(self, mock_repo, tmp_path):
        """Preserva .mcp.json se já existir."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        target.mkdir()

        existing_mcp = target / ".mcp.json"
        existing_mcp.write_text('{"mcpServers": {"postgres": "existing"}}\n')

        status = install_to_dir(mock_repo, target)

        assert status[".mcp.json"] is False  # preservado
        assert '"postgres": "existing"' in existing_mcp.read_text()

    def test_copies_mcp_json_if_missing(self, mock_repo, tmp_path):
        """Copia .mcp.json se não existir."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        status = install_to_dir(mock_repo, target)

        assert status[".mcp.json"] is True
        assert_file_exists(target / ".mcp.json")

    def test_copies_skills_and_commands_recursively(self, mock_repo, tmp_path):
        """Copia skills/ e commands/ recursivamente."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        status = install_to_dir(mock_repo, target)

        assert status["skills"] is True
        assert status["commands"] is True

        assert_file_exists(target / "skills" / "example.md")
        assert_file_exists(target / "commands" / "example.sh")

    def test_copies_tasks_only_if_missing(self, mock_repo, tmp_path):
        """Copia tasks/*.md apenas se não existirem."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        tasks_dir = target / "tasks"
        tasks_dir.mkdir(parents=True)

        # Criar apenas um arquivo existente
        existing_todo = tasks_dir / "todo.md"
        existing_todo.write_text("# EXISTING TODO\n")

        status = install_to_dir(mock_repo, target)

        # todo.md não foi copiado (preservado)
        assert status["tasks/todo.md"] is False
        assert "EXISTING TODO" in existing_todo.read_text()

        # lessons.md e decisions.md foram copiados
        assert status["tasks/lessons.md"] is True
        assert status["tasks/decisions.md"] is True
        assert_file_exists(tasks_dir / "lessons.md")
        assert_file_exists(tasks_dir / "decisions.md")

    def test_creates_audit_log(self, mock_repo, tmp_path):
        """Cria audit.log vazio."""
        from installer.files import install_to_dir

        target = tmp_path / ".claude"
        status = install_to_dir(mock_repo, target)

        assert status["audit.log"] is True
        assert_file_exists(target / "audit.log")
        assert (target / "audit.log").stat().st_size == 0


class TestMultipleAccountInstall:
    """Testes de instalação em múltiplas contas."""

    def test_installs_to_all_three_directories(self, mock_repo, tmp_path):
        """Instala em ~/.claude, ~/.claude-mprj, ~/.claude-pessoal."""
        from installer.files import install_to_dir

        for suffix in ["", "-mprj", "-pessoal"]:
            target = tmp_path / f".claude{suffix}"
            install_to_dir(mock_repo, target)
            assert_dir_exists(target)
            assert_file_exists(target / "CLAUDE.md")
            assert_file_exists(target / "settings.json")
