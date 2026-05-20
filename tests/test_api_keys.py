"""Testes de configuração de API keys via Infisical."""
import pytest


@pytest.fixture
def mock_load_secrets(monkeypatch):
    """Mock de secretsloader.load_secrets() com secrets de teste."""
    mock_secrets = {
        "ANTHROPIC_FOUNDRY_API_KEY": "sk-ant-test-foundry-key-1234",
        "GITLAB_TOKEN": "glpat-test-token-5678",
        "POSTMAN_API_KEY": "PMAK-test-key-9012",
    }

    def mock_func():
        return mock_secrets

    # Mock no módulo installer.api_keys
    monkeypatch.setattr("installer.api_keys.load_secrets", mock_func)

    return mock_secrets


class TestLoadSecrets:
    """Testes da função load_secrets()."""

    def test_loads_secrets_from_infisical(self, mock_load_secrets):
        """Carrega secrets do Infisical."""
        from installer.api_keys import load_secrets

        secrets = load_secrets()

        assert "ANTHROPIC_FOUNDRY_API_KEY" in secrets
        assert "GITLAB_TOKEN" in secrets
        assert "POSTMAN_API_KEY" in secrets


class TestConfigureFoundryKey:
    """Testes da função configure_foundry_key()."""

    def test_creates_key_file_on_linux(self, temp_home, mock_load_secrets, monkeypatch):
        """Linux: cria ~/.secrets/claude-mprj.key com chmod 600."""
        # Forçar Linux
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)

        from installer.api_keys import configure_foundry_key

        result = configure_foundry_key(temp_home)

        assert result is True

        key_file = temp_home / ".secrets" / "claude-mprj.key"
        assert key_file.exists()
        assert key_file.read_text() == "sk-ant-test-foundry-key-1234"

        # Verificar permissões
        assert key_file.stat().st_mode & 0o777 == 0o600

    def test_creates_secrets_dir_with_700(self, temp_home, mock_load_secrets, monkeypatch):
        """Linux: cria diretório .secrets com chmod 700."""
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)

        from installer.api_keys import configure_foundry_key

        configure_foundry_key(temp_home)

        secrets_dir = temp_home / ".secrets"
        assert secrets_dir.exists()
        assert secrets_dir.stat().st_mode & 0o777 == 0o700


class TestConfigureGitlabToken:
    """Testes da função configure_gitlab_token()."""

    def test_appends_to_bashrc_on_linux(
        self, temp_home, mock_load_secrets, monkeypatch
    ):
        """Linux: adiciona GITLAB_TOKEN ao .bashrc."""
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)
        monkeypatch.setattr("installer.api_keys.get_shell", lambda: "bash")

        from installer.api_keys import configure_gitlab_token

        result = configure_gitlab_token(temp_home)

        assert result is True

        bashrc = temp_home / ".bashrc"
        content = bashrc.read_text()

        assert 'export GITLAB_TOKEN="glpat-test-token-5678"' in content
        assert 'export GITLAB_URL="https://gitlab-dti.mprj.mp.br"' in content

    def test_appends_to_fish_config_on_linux(
        self, temp_home, mock_load_secrets, monkeypatch
    ):
        """Linux: adiciona GITLAB_TOKEN ao fish config."""
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)
        monkeypatch.setattr("installer.api_keys.get_shell", lambda: "fish")

        from installer.api_keys import configure_gitlab_token

        result = configure_gitlab_token(temp_home)

        assert result is True

        fish_config = temp_home / ".config" / "fish" / "conf.d" / "claude.fish"
        content = fish_config.read_text()

        assert 'set -x GITLAB_TOKEN "glpat-test-token-5678"' in content
        assert 'set -x GITLAB_URL "https://gitlab-dti.mprj.mp.br"' in content

    def test_does_not_duplicate_if_already_exists(
        self, temp_home, mock_load_secrets, monkeypatch
    ):
        """Não duplica variável se já existir."""
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)
        monkeypatch.setattr("installer.api_keys.get_shell", lambda: "bash")

        # Criar .bashrc com GITLAB_TOKEN já presente
        bashrc = temp_home / ".bashrc"
        bashrc.write_text('export GITLAB_TOKEN="existing-token"\n')

        from installer.api_keys import configure_gitlab_token

        configure_gitlab_token(temp_home)

        content = bashrc.read_text()

        # Verificar que não duplicou
        assert content.count("GITLAB_TOKEN") == 1
        assert 'export GITLAB_TOKEN="existing-token"' in content


class TestConfigurePostmanKey:
    """Testes da função configure_postman_key()."""

    def test_appends_to_bashrc_on_linux(
        self, temp_home, mock_load_secrets, monkeypatch
    ):
        """Linux: adiciona POSTMAN_API_KEY ao .bashrc."""
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)
        monkeypatch.setattr("installer.api_keys.get_shell", lambda: "bash")

        from installer.api_keys import configure_postman_key

        result = configure_postman_key(temp_home)

        assert result is True

        bashrc = temp_home / ".bashrc"
        content = bashrc.read_text()

        assert 'export POSTMAN_API_KEY="PMAK-test-key-9012"' in content

    def test_does_not_duplicate_if_already_exists(
        self, temp_home, mock_load_secrets, monkeypatch
    ):
        """Não duplica variável se já existir."""
        monkeypatch.setattr("installer.api_keys.is_windows", lambda: False)
        monkeypatch.setattr("installer.api_keys.get_shell", lambda: "bash")

        # Criar .bashrc com POSTMAN_API_KEY já presente
        bashrc = temp_home / ".bashrc"
        bashrc.write_text('export POSTMAN_API_KEY="existing-key"\n')

        from installer.api_keys import configure_postman_key

        configure_postman_key(temp_home)

        content = bashrc.read_text()

        # Verificar que não duplicou
        assert content.count("POSTMAN_API_KEY") == 1
        assert 'export POSTMAN_API_KEY="existing-key"' in content
