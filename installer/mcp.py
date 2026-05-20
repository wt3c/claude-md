"""
Instalação de MCP servers globais.

Equivalente a install_mcps() do install.sh (linhas 692-727).
"""

import os
import subprocess
from typing import Dict, List

# MCPs globais instalados com --scope user
MCP_SERVERS = {
    "filesystem": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "$HOME"],
    "memory": ["npx", "-y", "@modelcontextprotocol/server-memory"],
    "gitlab": ["npx", "-y", "@modelcontextprotocol/server-gitlab"],
    "postman": ["npx", "-y", "@postman/postman-mcp-server"],
}


def get_installed_mcps() -> List[str]:
    """
    Retorna lista de MCPs já instalados.

    Returns:
        Lista de nomes de MCPs (ex: ["filesystem", "memory"])
    """
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            check=True,
            text=True,
        )

        installed = []
        for line in result.stdout.splitlines():
            # Parse output de `claude mcp list`
            for mcp_name in MCP_SERVERS.keys():
                if mcp_name in line:
                    installed.append(mcp_name)

        return installed
    except subprocess.CalledProcessError:
        return []


def install_mcps() -> Dict[str, bool]:
    """
    Instala MCPs globais (filesystem, memory, gitlab, postman).

    Equivalente a install_mcps() do install.sh (linhas 692-727).

    Returns:
        Dict com status de cada MCP {name: bool(instalado_agora)}
        False = já estava instalado (pulado)
        True = instalado nesta execução

    Raises:
        RuntimeError: Se falha ao instalar algum MCP
    """
    status = {}
    installed = get_installed_mcps()

    for mcp_name, args in MCP_SERVERS.items():
        if mcp_name in installed:
            status[mcp_name] = False  # Já instalado
            continue

        # Substituir $HOME pelo path real
        args_resolved = [arg.replace("$HOME", os.path.expanduser("~")) for arg in args]

        try:
            subprocess.run(
                ["claude", "mcp", "add", "--scope", "user", mcp_name, "--"]
                + args_resolved,
                capture_output=True,
                check=True,
                text=True,
            )
            status[mcp_name] = True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Falha ao instalar MCP {mcp_name}: {e.stderr}"
            ) from e

    return status
