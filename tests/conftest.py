"""
Fixtures e configuração global para testes dos instaladores.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_home(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Cria um diretório HOME temporário isolado para testes.

    Estrutura criada:
    - .bashrc (vazio)
    - .zshrc (vazio)
    - .config/fish/conf.d/ (dir)
    """
    home = tmp_path / "home"
    home.mkdir()

    # Criar arquivos rc vazios
    (home / ".bashrc").touch()
    (home / ".zshrc").touch()

    # Criar diretório fish
    fish_conf = home / ".config" / "fish" / "conf.d"
    fish_conf.mkdir(parents=True)

    # Criar diretório .secrets
    (home / ".secrets").mkdir(mode=0o700)

    yield home


@pytest.fixture
def mock_repo(tmp_path: Path) -> Path:
    """
    Cria um repositório mock com estrutura mínima necessária.

    Contém:
    - CLAUDE.md
    - settings.json
    - .mcp.json
    - skills/ (dir com arquivo dummy)
    - commands/ (dir com arquivo dummy)
    - tasks/ (todo.md, lessons.md, decisions.md)
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    # Arquivos principais
    (repo / "CLAUDE.md").write_text("# CLAUDE.md mock\n")
    (repo / "settings.json").write_text('{"version": "mock"}\n')
    (repo / ".mcp.json").write_text('{"mcpServers": {}}\n')

    # Skills e commands
    skills_dir = repo / "skills"
    skills_dir.mkdir()
    (skills_dir / "example.md").write_text("# Example skill\n")

    commands_dir = repo / "commands"
    commands_dir.mkdir()
    (commands_dir / "example.sh").write_text("#!/bin/bash\necho example\n")

    # Tasks
    tasks_dir = repo / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "todo.md").write_text("# TODO\n")
    (tasks_dir / "lessons.md").write_text("# Lessons\n")
    (tasks_dir / "decisions.md").write_text("# Decisions\n")

    return repo


@pytest.fixture
def existing_secrets(temp_home: Path) -> dict[str, Path]:
    """
    Cria arquivos sensíveis existentes no HOME temporário.

    Retorna um dicionário com os paths criados para validação posterior.
    """
    secrets = {}

    # Linux secret
    key_file = temp_home / ".secrets" / "claude-mprj.key"
    key_file.write_text("sk-ant-existing-key-1234")
    key_file.chmod(0o600)
    secrets["key"] = key_file

    # Credentials
    for account in ["", "-mprj", "-pessoal"]:
        dir_path = temp_home / f".claude{account}"
        dir_path.mkdir(parents=True, exist_ok=True)

        # Usar sufixo vazio para conta principal
        suffix = account if account else ""

        creds = dir_path / ".credentials.json"
        creds.write_text('{"existing": true}')
        secrets[f"creds{suffix}"] = creds

        claude_json = dir_path / ".claude.json"
        claude_json.write_text('{"existing": true}')
        secrets[f"claude{suffix}"] = claude_json

        model_cache = dir_path / ".model-cache.json"
        model_cache.write_text('{"model": "existing"}')
        secrets[f"model{suffix}"] = model_cache

        local_settings = dir_path / "settings.local.json"
        local_settings.write_text('{"local": true}')
        secrets[f"local{suffix}"] = local_settings

        mcp = dir_path / ".mcp.json"
        mcp.write_text('{"mcpServers": {"postgres": "existing"}}')
        secrets[f"mcp{suffix}"] = mcp

    return secrets


@pytest.fixture
def mock_commands(monkeypatch) -> dict[str, Mock]:
    """
    Mock de comandos externos (git, node, claude).

    Retorna um dicionário com os mocks para customização nos testes.
    """
    mocks = {
        "git": Mock(return_value=subprocess.CompletedProcess(
            args=["git", "--version"],
            returncode=0,
            stdout=b"git version 2.43.0\n",
            stderr=b""
        )),
        "node": Mock(return_value=subprocess.CompletedProcess(
            args=["node", "--version"],
            returncode=0,
            stdout=b"v20.11.0\n",
            stderr=b""
        )),
        "claude": Mock(return_value=subprocess.CompletedProcess(
            args=["claude", "--version"],
            returncode=0,
            stdout=b"claude-code 0.7.0\n",
            stderr=b""
        )),
    }

    def mock_run(args, *run_args, **run_kwargs):
        cmd = args[0] if isinstance(args, list) else args.split()[0]
        if cmd in mocks:
            return mocks[cmd].return_value
        # Deixa outros comandos passarem
        return subprocess.run(args, *run_args, **run_kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    return mocks


@pytest.fixture
def installer_env(temp_home: Path, mock_repo: Path, monkeypatch) -> dict:
    """
    Configura ambiente completo para execução de instaladores.

    Retorna um dict com:
    - home: Path do HOME temporário
    - repo: Path do repositório mock
    - backup_root: Path onde backups serão criados
    """
    backup_root = temp_home / ".claude-md-backups"

    # Set HOME env var
    monkeypatch.setenv("HOME", str(temp_home))
    monkeypatch.setenv("USERPROFILE", str(temp_home))  # Windows

    return {
        "home": temp_home,
        "repo": mock_repo,
        "backup_root": backup_root,
    }


@pytest.fixture
def shell_rc_with_legacy_block(temp_home: Path) -> Path:
    """
    Cria um .bashrc com bloco legacy (v1) das funções claude.
    """
    bashrc = temp_home / ".bashrc"
    bashrc.write_text("""
# Other content
export PATH=/usr/local/bin:$PATH

# --- Claude Code: múltiplas contas ---
function claude-mprj() {
    # legacy version without v=2
    echo "old version"
}
# --- end Claude Code multi-conta ---

# More content
alias ll='ls -la'
""")
    return bashrc


@pytest.fixture
def shell_rc_with_v2_block(temp_home: Path) -> Path:
    """
    Cria um .bashrc com bloco v2 (atual) das funções claude.
    """
    bashrc = temp_home / ".bashrc"
    bashrc.write_text("""
# Other content
export PATH=/usr/local/bin:$PATH

# --- Claude Code: múltiplas contas (v=2) ---
function claude-mprj() {
    # current version with v=2
    echo "new version"
}
# --- end Claude Code multi-conta ---

# More content
alias ll='ls -la'
""")
    return bashrc


def run_install_sh(
    repo_dir: Path,
    home_dir: Path,
    inputs: list[str] | None = None,
    env: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    """
    Executa install.sh com inputs simulados.

    Args:
        repo_dir: Diretório do repositório
        home_dir: Diretório HOME temporário
        inputs: Lista de inputs para stdin (um por linha)
        env: Variáveis de ambiente adicionais

    Returns:
        CompletedProcess com resultado da execução
    """
    script = repo_dir / "install.sh"

    # Preparar env
    test_env = os.environ.copy()
    test_env["HOME"] = str(home_dir)
    if env:
        test_env.update(env)

    # Preparar stdin
    stdin_data = "\n".join(inputs) + "\n" if inputs else ""

    return subprocess.run(
        ["bash", str(script)],
        cwd=str(repo_dir),
        input=stdin_data.encode(),
        capture_output=True,
        env=test_env,
    )


def run_install_ps1(
    repo_dir: Path,
    home_dir: Path,
    inputs: list[str] | None = None,
    env: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    """
    Executa install.ps1 com inputs simulados.

    Args:
        repo_dir: Diretório do repositório
        home_dir: Diretório HOME temporário
        inputs: Lista de inputs para stdin
        env: Variáveis de ambiente adicionais

    Returns:
        CompletedProcess com resultado da execução
    """
    script = repo_dir / "install.ps1"

    # Preparar env
    test_env = os.environ.copy()
    test_env["USERPROFILE"] = str(home_dir)
    test_env["HOME"] = str(home_dir)
    if env:
        test_env.update(env)

    # Preparar stdin
    stdin_data = "\n".join(inputs) + "\n" if inputs else ""

    return subprocess.run(
        ["pwsh", "-File", str(script)],
        cwd=str(repo_dir),
        input=stdin_data.encode(),
        capture_output=True,
        env=test_env,
    )


# Helpers para validação
def assert_file_exists(path: Path, msg: str = ""):
    """Assert que arquivo existe."""
    assert path.exists() and path.is_file(), msg or f"File should exist: {path}"


def assert_dir_exists(path: Path, msg: str = ""):
    """Assert que diretório existe."""
    assert path.exists() and path.is_dir(), msg or f"Directory should exist: {path}"


def assert_file_content_contains(path: Path, content: str, msg: str = ""):
    """Assert que arquivo contém texto específico."""
    assert path.exists(), f"File should exist: {path}"
    actual = path.read_text()
    assert content in actual, msg or f"File should contain '{content}', got:\n{actual}"


def assert_file_mode(path: Path, mode: int):
    """Assert que arquivo tem permissões específicas."""
    assert path.exists(), f"File should exist: {path}"
    actual_mode = path.stat().st_mode & 0o777
    assert actual_mode == mode, f"File mode should be {oct(mode)}, got {oct(actual_mode)}"
