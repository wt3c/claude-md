"""
Desinstalação completa do Claude Code multi-conta.

Remove configurações, arquivos, integrações shell e faz backup antes de remover.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from installer.backup import backup_secrets
from installer.platform import get_home, is_windows
from installer.shell_config import remove_shell_block


def get_paths_to_remove(home: Path) -> List[Tuple[Path, str]]:
    """
    Retorna lista de paths a remover com descrição.

    Returns:
        Lista de tuplas (path, descrição)
    """
    paths = [
        (home / ".claude-pessoal", "Configuração Claude pessoal"),
        (home / ".claude-mprj", "Configuração Claude MPRJ"),
        (home / ".claude", "Configuração Claude global"),
    ]

    # Linux: adicionar chave Foundry
    if not is_windows():
        paths.append(
            (home / ".secrets" / "claude-mprj.key", "Chave API MPRJ Foundry")
        )

    return paths


def get_shell_files_to_clean(home: Path) -> List[Tuple[Path, str]]:
    """
    Retorna lista de arquivos shell a limpar.

    Returns:
        Lista de tuplas (path, descrição)
    """
    if is_windows():
        # PowerShell profile
        documents = Path(home) / "Documents"
        return [
            (
                documents / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1",
                "PowerShell profile",
            ),
            (
                documents / "PowerShell" / "Microsoft.PowerShell_profile.ps1",
                "PowerShell 7+ profile",
            ),
        ]
    else:
        # Linux: bash, zsh, fish
        return [
            (home / ".bashrc", "Bash config"),
            (home / ".zshrc", "Zsh config"),
            (home / ".config" / "fish" / "conf.d" / "claude.fish", "Fish config"),
        ]


def preview_removal(home: Path) -> Tuple[List[Path], List[Path], int]:
    """
    Mostra o que será removido e retorna contagem.

    Returns:
        Tupla (paths_existentes, shell_files_existentes, total_size_bytes)
    """
    print("\n" + "=" * 70)
    print("PREVIEW DE DESINSTALAÇÃO")
    print("=" * 70)

    # Diretórios e arquivos de configuração
    print("\n📁 Diretórios e arquivos a remover:")
    paths_to_remove = get_paths_to_remove(home)
    existing_paths = []
    total_size = 0

    for path, desc in paths_to_remove:
        if path.exists():
            existing_paths.append(path)
            if path.is_dir():
                # Calcular tamanho do diretório
                size = sum(
                    f.stat().st_size for f in path.rglob("*") if f.is_file()
                )
                total_size += size
                size_mb = size / (1024 * 1024)
                print(f"  ✓ {path} ({desc}) - {size_mb:.2f} MB")
            else:
                size = path.stat().st_size
                total_size += size
                size_kb = size / 1024
                print(f"  ✓ {path} ({desc}) - {size_kb:.2f} KB")
        else:
            print(f"  ✗ {path} ({desc}) - não existe")

    # Arquivos shell a limpar
    print("\n🐚 Arquivos shell a limpar (blocos de configuração):")
    shell_files = get_shell_files_to_clean(home)
    existing_shell_files = []

    for path, desc in shell_files:
        if path.exists():
            existing_shell_files.append(path)
            print(f"  ✓ {path} ({desc})")
        else:
            print(f"  ✗ {path} ({desc}) - não existe")

    # Resumo
    total_mb = total_size / (1024 * 1024)
    print("\n" + "=" * 70)
    print(f"TOTAL: {len(existing_paths)} paths, {len(existing_shell_files)} "
          f"arquivos shell, ~{total_mb:.2f} MB")
    print("=" * 70)

    return existing_paths, existing_shell_files, total_size


def confirm_removal() -> bool:
    """
    Pede confirmação do usuário.

    Returns:
        True se confirmado, False caso contrário
    """
    print("\n⚠️  ATENÇÃO: Esta ação é irreversível!")
    print("Um backup será criado antes da remoção em ~/.claude-backups/")
    print("\nDeseja continuar? [s/N]: ", end="")

    try:
        response = input().strip().lower()
        return response in ["s", "sim", "y", "yes"]
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperação cancelada pelo usuário.")
        return False


def remove_shell_configs(shell_files: List[Path]) -> None:
    """
    Remove blocos de configuração dos arquivos shell.

    Args:
        shell_files: Lista de arquivos shell a limpar
    """
    print("\n🐚 Removendo configurações shell...")

    for path in shell_files:
        if not path.exists():
            continue

        # Fish: remover arquivo completo
        if path.name == "claude.fish":
            backup = path.parent / f"claude.fish.uninstall-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            shutil.copy2(path, backup)
            path.unlink()
            print(f"  ✓ Removido: {path}")
            print(f"    Backup: {backup}")
        else:
            # Bash/Zsh/PowerShell: remover bloco
            backup_file = remove_shell_block(path)
            if backup_file:
                print(f"  ✓ Bloco removido de: {path}")
                print(f"    Backup: {backup_file}")
            else:
                print(f"  ℹ Nenhum bloco encontrado em: {path}")


def remove_paths(paths: List[Path]) -> None:
    """
    Remove paths (diretórios e arquivos).

    Args:
        paths: Lista de paths a remover
    """
    print("\n📁 Removendo configurações...")

    for path in paths:
        if not path.exists():
            continue

        try:
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  ✓ Removido diretório: {path}")
            else:
                path.unlink()
                print(f"  ✓ Removido arquivo: {path}")
        except Exception as e:
            print(f"  ✗ Erro ao remover {path}: {e}", file=sys.stderr)


def main() -> None:
    """
    Função principal de desinstalação.
    """
    print("\n🗑️  DESINSTALADOR CLAUDE CODE MULTI-CONTA")
    print("=" * 70)

    home = get_home()

    # Preview
    existing_paths, existing_shell_files, total_size = preview_removal(home)

    # Verificar se há algo para remover
    if not existing_paths and not existing_shell_files:
        print("\n✓ Nenhuma configuração encontrada. Sistema já está limpo.")
        sys.exit(0)

    # Confirmação
    if not confirm_removal():
        print("\n✓ Operação cancelada. Nenhuma alteração foi feita.")
        sys.exit(0)

    # Criar backup
    print("\n💾 Criando backup...")
    backup_root = home / ".claude-backups"
    try:
        backup_dir = backup_secrets(home, backup_root)
        print(f"  ✓ Backup criado em: {backup_dir}")
    except Exception as e:
        print(f"  ✗ Erro ao criar backup: {e}", file=sys.stderr)
        print("\n⚠️  Deseja continuar sem backup? [s/N]: ", end="")
        response = input().strip().lower()
        if response not in ["s", "sim", "y", "yes"]:
            print("\n✓ Operação cancelada.")
            sys.exit(1)

    # Remover configurações shell
    if existing_shell_files:
        remove_shell_configs(existing_shell_files)

    # Remover paths
    if existing_paths:
        remove_paths(existing_paths)

    # Resumo final
    print("\n" + "=" * 70)
    print("✓ DESINSTALAÇÃO CONCLUÍDA")
    print("=" * 70)
    print(f"\n💾 Backup disponível em: {backup_dir}")
    print("\nPara restaurar, copie manualmente os arquivos do backup.")
    print("\nPara completar a limpeza, reinicie o shell ou execute:")

    if is_windows():
        print("  . $PROFILE")
    else:
        print("  source ~/.bashrc  # ou ~/.zshrc, ou reinicie o terminal")

    print("\n👋 Claude Code foi removido do sistema.")
