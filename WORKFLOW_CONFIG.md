# Workflow de Mudanças em Configurações Claude Code

## Pipeline Obrigatório

Toda alteração em configurações globais do Claude Code deve seguir este fluxo:

```
1. Testar em ~/.claude/
   ↓ (validar funcionamento)
2. Copiar para ambientes específicos
   ├── ~/.claude-mprj/ (MPRJ - Azure Foundry)
   └── ~/.claude-pessoal/ (Pessoal - anthropic.com)
   ↓ (adaptar para SO quando necessário)
3. Versionar em ~/workspace/claude-md/
   ↓
4. Commit e push
```

## Arquivos Afetados

- `settings.json` — modelo, permissões, hooks, MCP servers
- `CLAUDE.md` — instruções globais e de projeto
- `keybindings.json` — atalhos de teclado
- `hooks/` — scripts de automação
- Qualquer outra configuração do Claude Code

## Exemplo Prático

```bash
# 1. Testar mudança
vim ~/.claude/settings.json
claude-pro --model opus "teste rápido"  # valida que funciona

# 2. Propagar para ambientes específicos
cp ~/.claude/settings.json ~/.claude-mprj/
cp ~/.claude/settings.json ~/.claude-pessoal/

# 3. Versionar
cp ~/.claude/settings.json ~/workspace/claude-md/settings.json
cd ~/workspace/claude-md

# 4. Commitar
git add settings.json
git commit -m "config: adicionar subagentModel haiku"
git push
```

## Por Quê?

- **Segurança**: Ambiente `~/.claude/` é staging, evita quebrar produção
- **Rastreabilidade**: Git mantém histórico de mudanças
- **Consistência**: Garante que todos os ambientes têm configurações validadas
- **Recuperação**: Se algo quebrar, basta reverter o commit

## Integração com Instalação

Este workflow deve ser explicado durante o setup inicial (`install.sh` ou equivalente) e referenciado na memória global do Claude para que seja seguido automaticamente.

---

**Importante**: Nunca modificar diretamente `~/.claude-mprj/` ou `~/.claude-pessoal/` sem testar em `~/.claude/` primeiro.
