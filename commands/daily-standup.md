---
description: Gera resumo do dia para standup a partir de git log e tarefas ativas
---

Gere um resumo conciso para o standup diário com base em:

1. **Git log das últimas 24h** (rodar: `git log --since="24 hours ago" --oneline --author="$(git config user.name)"`)
2. **Conteúdo de tasks/todo.md** — o que estava planejado vs o que foi feito
3. **Status do último pipeline** (se MCP GitLab disponível)

## Formato de saída

```
FEITO (ontem/hoje):
- [item conciso baseado nos commits]

HOJE:
- [próximas etapas do tasks/todo.md]

BLOQUEIOS:
- [listar se houver, caso contrário: "Nenhum"]
```

Manter cada item em 1 linha. Total: máximo 10 linhas.
Idioma: português.
