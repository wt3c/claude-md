"""
Configuração de API keys via Infisical.

Equivalente a configure_api_key(), configure_gitlab(), configure_postman_key().
"""

import os
import re
from pathlib import Path
from typing import Dict

from installer.platform import get_shell, is_windows


def load_secrets() -> Dict[str, str]:
    """
    Carrega secrets do Infisical via secretsloader.

    Returns:
        Dict com secrets carregados

    Raises:
        RuntimeError: Se secretsloader falhar ou secrets não encontrados
    """
    try:
        from secretsloader import load_secrets as _load_secrets

        secrets = _load_secrets()

        # Verificar secrets obrigatórios
        required = ["ANTHROPIC_FOUNDRY_API_KEY", "GITLAB_TOKEN", "POSTMAN_API_KEY"]
        missing = [key for key in required if key not in secrets]

        if missing:
            raise RuntimeError(
                f"Secrets não encontrados no Infisical: {', '.join(missing)}. "
                "Configure no projeto Infisical primeiro."
            )

        return secrets
    except ImportError as e:
        raise RuntimeError(
            "secretsloader não instalado. Instale com: uv add secretsloader"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Falha ao carregar secrets do Infisical: {e}") from e


def configure_foundry_key(home: Path) -> bool:
    """
    Configura API Key Foundry (MPRJ).

    Linux: Salva em ~/.secrets/claude-mprj.key (chmod 600)
    Windows: Salva em variável de ambiente User

    Equivalente a configure_api_key() do install.sh (linhas 552-586).

    Args:
        home: Diretório HOME

    Returns:
        True se configurado

    Raises:
        RuntimeError: Se falha ao configurar
    """
    secrets = load_secrets()
    api_key = secrets["ANTHROPIC_FOUNDRY_API_KEY"]

    if is_windows():
        # Windows: variável de ambiente User
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE
            ) as reg_key:
                winreg.SetValueEx(
                    reg_key, "ANTHROPIC_FOUNDRY_API_KEY", 0, winreg.REG_SZ, api_key
                )
        except Exception as e:
            raise RuntimeError(
                f"Falha ao configurar ANTHROPIC_FOUNDRY_API_KEY no registro: {e}"
            ) from e
    else:
        # Linux: arquivo ~/.secrets/claude-mprj.key
        secrets_dir = home / ".secrets"
        secrets_dir.mkdir(mode=0o700, exist_ok=True)

        key_file = secrets_dir / "claude-mprj.key"
        key_file.write_text(api_key)
        key_file.chmod(0o600)

    return True


def configure_gitlab_token(home: Path) -> bool:
    """
    Configura GITLAB_TOKEN via Infisical.

    Equivalente a configure_gitlab() do install.sh (linhas 589-640).

    Args:
        home: Diretório HOME

    Returns:
        True se configurado

    Raises:
        RuntimeError: Se falha ao configurar
    """
    secrets = load_secrets()
    gitlab_token = secrets["GITLAB_TOKEN"]

    shell = get_shell()
    rc_file = _get_rc_file_for_env_var(shell, home)

    if is_windows():
        # Windows: variável de ambiente User
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE
            ) as reg_key:
                winreg.SetValueEx(
                    reg_key, "GITLAB_TOKEN", 0, winreg.REG_SZ, gitlab_token
                )
                winreg.SetValueEx(
                    reg_key,
                    "GITLAB_URL",
                    0,
                    winreg.REG_SZ,
                    "https://gitlab-dti.mprj.mp.br",
                )
        except Exception as e:
            raise RuntimeError(f"Falha ao configurar GITLAB_TOKEN no registro: {e}") from e
    else:
        # Linux: append ao rc file
        _append_env_var_to_rc(
            rc_file, "GITLAB_TOKEN", gitlab_token, shell_type=shell
        )
        _append_env_var_to_rc(
            rc_file, "GITLAB_URL", "https://gitlab-dti.mprj.mp.br", shell_type=shell
        )

    return True


def configure_postman_key(home: Path) -> bool:
    """
    Configura POSTMAN_API_KEY via Infisical.

    Equivalente a configure_postman_key() do install.sh (linhas 643-689).

    Args:
        home: Diretório HOME

    Returns:
        True se configurado

    Raises:
        RuntimeError: Se falha ao configurar
    """
    secrets = load_secrets()
    postman_key = secrets["POSTMAN_API_KEY"]

    shell = get_shell()
    rc_file = _get_rc_file_for_env_var(shell, home)

    if is_windows():
        # Windows: variável de ambiente User
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE
            ) as reg_key:
                winreg.SetValueEx(
                    reg_key, "POSTMAN_API_KEY", 0, winreg.REG_SZ, postman_key
                )
        except Exception as e:
            raise RuntimeError(
                f"Falha ao configurar POSTMAN_API_KEY no registro: {e}"
            ) from e
    else:
        # Linux: append ao rc file
        _append_env_var_to_rc(rc_file, "POSTMAN_API_KEY", postman_key, shell_type=shell)

    return True


def _get_rc_file_for_env_var(shell: str, home: Path) -> Path:
    """
    Retorna arquivo rc apropriado para definir variáveis de ambiente.
    """
    from installer.platform import get_rc_file

    return get_rc_file(shell, home)  # type: ignore[arg-type]


def _append_env_var_to_rc(rc_file: Path, var_name: str, value: str, *, shell_type: str) -> None:
    """
    Adiciona variável de ambiente ao arquivo rc se não existir.

    Args:
        rc_file: Arquivo rc
        var_name: Nome da variável
        value: Valor da variável
        shell_type: Tipo de shell ("bash", "zsh", "fish")
    """
    # Verificar se variável já existe
    if rc_file.exists():
        content = rc_file.read_text()
        # Regex para detectar export VAR ou set -x VAR
        pattern = rf"(export {var_name}|set -x {var_name})\s*="
        if re.search(pattern, content):
            # Já existe, não adicionar
            return

    # Adicionar variável
    rc_file.parent.mkdir(parents=True, exist_ok=True)

    if shell_type == "fish":
        line = f'\nset -x {var_name} "{value}"\n'
    else:
        line = f'\nexport {var_name}="{value}"\n'

    with rc_file.open("a") as f:
        f.write(line)
