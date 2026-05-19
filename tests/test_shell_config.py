"""Testes de configuração de shell."""
import pytest

from .conftest import assert_file_content_contains


class TestShellBlockDetection:
    """Testes de detecção de versão do bloco shell."""

    def test_detects_v2_block(self, shell_rc_with_v2_block):
        """Detecta bloco v2 presente."""
        from .test_helpers import detect_shell_block_version

        version = detect_shell_block_version(shell_rc_with_v2_block)
        assert version == "v2"

    def test_detects_v1_block(self, shell_rc_with_legacy_block):
        """Detecta bloco v1 (legacy) presente."""
        from .test_helpers import detect_shell_block_version

        version = detect_shell_block_version(shell_rc_with_legacy_block)
        assert version == "v1"

    def test_detects_no_block(self, temp_home):
        """Detecta ausência de bloco."""
        from .test_helpers import detect_shell_block_version

        bashrc = temp_home / ".bashrc"
        bashrc.write_text("# Just regular content\nexport PATH=/usr/bin:$PATH\n")

        version = detect_shell_block_version(bashrc)
        assert version is None


class TestShellBlockRemoval:
    """Testes de remoção de bloco shell."""

    def test_removes_legacy_block(self, shell_rc_with_legacy_block):
        """Remove bloco legacy e cria backup."""
        from .test_helpers import remove_shell_block

        original_content = shell_rc_with_legacy_block.read_text()

        backup = remove_shell_block(shell_rc_with_legacy_block)

        # Backup criado
        assert backup.exists()
        assert backup.read_text() == original_content

        # Bloco removido
        new_content = shell_rc_with_legacy_block.read_text()
        assert "Claude Code: múltiplas contas" not in new_content
        assert "claude-mprj" not in new_content

        # Conteúdo externo preservado
        assert "export PATH=/usr/local/bin:$PATH" in new_content
        assert "alias ll='ls -la'" in new_content

    def test_backup_has_timestamp(self, shell_rc_with_legacy_block):
        """Backup tem timestamp no nome."""
        from .test_helpers import remove_shell_block
        import re

        backup = remove_shell_block(shell_rc_with_legacy_block)

        # Validar formato: .bashrc.before-update-YYYYMMDD-HHMMSS
        pattern = r'\.before-update-\d{8}-\d{6}$'
        assert re.search(pattern, str(backup))


class TestShellBlockInsertion:
    """Testes de inserção de bloco shell (conceitual)."""

    def test_does_not_duplicate_v2_block(self, shell_rc_with_v2_block):
        """Não insere bloco se v2 já presente."""
        from .test_helpers import detect_shell_block_version

        # Simula a verificação antes de inserir
        version = detect_shell_block_version(shell_rc_with_v2_block)
        should_insert = (version != "v2")

        assert not should_insert, "Should not insert if v2 already present"

    def test_prompts_migration_for_v1_block(self, shell_rc_with_legacy_block):
        """Deve perguntar ao usuário se detectar v1."""
        from .test_helpers import detect_shell_block_version

        version = detect_shell_block_version(shell_rc_with_legacy_block)
        should_prompt = (version == "v1")

        assert should_prompt, "Should prompt user to migrate v1 to v2"
