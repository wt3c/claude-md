"""
CLI principal com Rich (menus, progresso, tabelas).

Orquestra todos os módulos de instalação.
"""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

console = Console()


@click.command()
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Modo não-interativo (CI/CD)",
)
@click.option(
    "--multi-account",
    is_flag=True,
    help="Configurar múltiplas contas (MPRJ + Pessoal)",
)
@click.option(
    "--update-only",
    is_flag=True,
    help="Atualizar apenas arquivos (preservar configs)",
)
@click.option(
    "--mcps-only",
    is_flag=True,
    help="Instalar apenas MCP servers",
)
def main(
    non_interactive: bool,
    multi_account: bool,
    update_only: bool,
    mcps_only: bool,
) -> None:
    """
    Claude Code — Instalação Global (Python)

    Substitui install.sh e install.ps1 com instalador unificado Python.
    """
    import sys

    # Header
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Claude Code — Instalação Global (Python)[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    # Detectar ambiente
    home = Path.home()
    repo_dir = Path(__file__).parent.parent  # claude-md/
    backup_root = home / ".claude-md-backups"

    # 1. Verificar pré-requisitos
    console.print("[cyan]▶[/cyan]  Verificando pré-requisitos...")

    try:
        from installer.prereqs import check_prereqs

        prereqs = check_prereqs()

        console.print(f"[green]✔[/green]  Git {prereqs['git']}")
        console.print(f"[green]✔[/green]  Node.js v{prereqs['node']}")
        console.print(f"[green]✔[/green]  Claude Code {prereqs['claude']}")
    except RuntimeError as e:
        console.print(f"[red]✖[/red]  {e}", style="bold red")
        sys.exit(1)

    console.print()

    # 2. Atualizar repositório
    console.print("[cyan]▶[/cyan]  Atualizando repositório...")
    from installer.files import update_repo

    if update_repo(repo_dir):
        console.print("[green]✔[/green]  Repositório atualizado")
    else:
        console.print(
            "[yellow]⚠[/yellow]  Pull falhou — continuando com versão local"
        )

    console.print()

    # 3. Backup de secrets
    console.print(
        "[cyan]▶[/cyan]  Snapshot de chaves e credenciais (BEFORE install)..."
    )

    from installer.backup import backup_secrets, get_sensitive_files

    sensitive_count = len(get_sensitive_files(home))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Copiando arquivos sensíveis...", total=sensitive_count
        )

        backup_dir = backup_secrets(home, backup_root)

        progress.update(task, completed=sensitive_count)

    console.print(
        f"[green]✔[/green]  {sensitive_count} arquivo(s) sensível(is) "
        f"preservados em {backup_dir}"
    )
    console.print()

    # 4. Instalação
    if not mcps_only:
        # Perguntar sobre múltiplas contas (se não especificado)
        if not non_interactive and not multi_account:
            multi_account = Confirm.ask(
                "Configurar múltiplas contas (MPRJ + Pessoal)?", default=True
            )

        # Instalar ~/.claude
        console.print("[cyan]▶[/cyan]  Instalando em ~/.claude ...")

        from installer.files import install_to_dir

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Instalando arquivos...", total=None)

            install_to_dir(repo_dir, home / ".claude")

            progress.update(task, completed=1)

        console.print("[green]✔[/green]  ~/.claude configurado")
        console.print()

        if multi_account:
            # Instalar ~/.claude-mprj e ~/.claude-pessoal
            for account in ["mprj", "pessoal"]:
                console.print(
                    f"[cyan]▶[/cyan]  Instalando em ~/.claude-{account} ..."
                )

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Instalando arquivos...", total=None)

                    install_to_dir(repo_dir, home / f".claude-{account}")

                    progress.update(task, completed=1)

                console.print(f"[green]✔[/green]  ~/.claude-{account} configurado")
                console.print()

            # Configurar API keys via Infisical
            console.print("[cyan]▶[/cyan]  Configurando API Keys via Infisical...")

            from installer.api_keys import (
                configure_foundry_key,
                configure_gitlab_token,
            )

            try:
                configure_foundry_key(home)
                console.print("[green]✔[/green]  Foundry API Key configurada")

                configure_gitlab_token(home)
                console.print("[green]✔[/green]  GitLab Token configurado")
            except RuntimeError as e:
                console.print(f"[red]✖[/red]  {e}", style="bold red")
                sys.exit(1)

            console.print()

            # Configurar shell
            if not non_interactive:
                from installer.platform import get_shell
                from installer.shell_config import install_shell_block

                shell = get_shell()
                configure_shell = Confirm.ask(
                    f"Configurar funções shell ({shell})?", default=True
                )

                if configure_shell:
                    console.print(f"[cyan]▶[/cyan]  Configurando {shell}...")
                    rc_file = install_shell_block(shell, home)
                    console.print(f"[green]✔[/green]  {shell} configurado")
                    console.print(
                        f"[dim]    Arquivo: {rc_file}[/dim]"
                    )
                    console.print()

    # 5. MCP servers
    if not update_only:
        install_mcps_flag = mcps_only or (
            not non_interactive
            and Confirm.ask(
                "Instalar MCP servers globais (filesystem, memory, gitlab, postman)?",
                default=True,
            )
        )

        if install_mcps_flag:
            console.print("[cyan]▶[/cyan]  Instalando MCP servers globais...")

            from installer.mcp import install_mcps

            try:
                mcp_status = install_mcps()

                for mcp_name, installed in mcp_status.items():
                    if installed:
                        console.print(f"[green]✔[/green]  MCP {mcp_name} instalado")
                    else:
                        console.print(
                            f"[yellow]⚠[/yellow]  MCP {mcp_name} já instalado — pulando"
                        )
            except RuntimeError as e:
                console.print(f"[red]✖[/red]  {e}", style="bold red")
                if not non_interactive:
                    if not Confirm.ask("Continuar sem MCPs?", default=True):
                        sys.exit(1)

            console.print()

            # Configurar Postman API Key
            if multi_account and not non_interactive:
                console.print(
                    "[cyan]▶[/cyan]  Configurando Postman API Key via Infisical..."
                )

                from installer.api_keys import configure_postman_key

                try:
                    configure_postman_key(home)
                    console.print("[green]✔[/green]  Postman API Key configurada")
                except RuntimeError as e:
                    console.print(f"[yellow]⚠[/yellow]  {e}")

                console.print()

    # 6. Restore de secrets
    console.print(
        "[cyan]▶[/cyan]  Verificação pós-instalação: "
        "restaurando chaves se faltarem..."
    )

    from installer.backup import restore_secrets

    restored = restore_secrets(home, backup_dir)

    if restored == 0:
        console.print(
            "[green]✔[/green]  Nada para restaurar — "
            "arquivos sensíveis preservados intactos"
        )
    else:
        console.print(f"[green]✔[/green]  {restored} arquivo(s) restaurado(s) do backup")

    console.print(f"[cyan]▶[/cyan]  Backup completo permanece em: {backup_dir}")
    console.print()

    # 7. Resumo final
    console.print("[bold green]✔ Instalação concluída![/bold green]\n")

    if multi_account:
        console.print("  [bold]Próximos passos:[/bold]")

        from installer.platform import get_shell
        shell = get_shell()

        if shell == "fish":
            reload_cmd = "source ~/.config/fish/config.fish"
        elif shell == "zsh":
            reload_cmd = "source ~/.zshrc"
        else:
            reload_cmd = "source ~/.bashrc"

        console.print(f"  1. Recarregar shell:    [cyan]{reload_cmd}[/cyan]")
        console.print("  2. Autenticar MPRJ:     [cyan]claude-mprj[/cyan]")
        console.print("  3. Autenticar pessoal:  [cyan]claude-pro  →  /login[/cyan]")
        console.print()
        console.print("  [bold]Token GitLab:[/bold]")
        console.print(
            "  https://gitlab-dti.mprj.mp.br/-/user_settings/personal_access_tokens"
        )
    else:
        console.print("  [bold]Próximos passos:[/bold]")
        console.print("  1. Execute: [cyan]claude[/cyan]")

    console.print()
    console.print("  [bold yellow]⚠ Workflow de Mudanças em Configurações:[/bold yellow]")
    console.print(
        "  Sempre testar mudanças em ~/.claude/ antes de propagar para os ambientes."
    )
    console.print("  Veja: WORKFLOW_CONFIG.md ou ~/.claude/WORKFLOW_CONFIG.md")
    console.print()


if __name__ == "__main__":
    main()
