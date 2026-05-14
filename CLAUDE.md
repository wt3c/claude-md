# CLAUDE.md — Configuração Global

<!-- Cache marker: stable-root-v3 -->

---

## ⚡ Bootstrap de Sessão (executar SEMPRE ao iniciar)

```
1. Ler tasks/lessons.md  — absorver padrões e antipadrões acumulados
2. Ler tasks/todo.md     — retomar contexto da última tarefa ativa
3. Confirmar stack ativa → carregar skill correspondente abaixo
4. Tarefas 3+ etapas → escrever plano em tasks/todo.md antes de implementar
```

> Se `tasks/` não existir: criar a estrutura antes de qualquer outra ação.

---

## 🧠 Skills — Carregar antes de qualquer tarefa não trivial

<!-- CACHE_MARKER: skills-stable -->

| Contexto                       | Skill                                         |
|--------------------------------|-----------------------------------------------|
| Python / Django / DRF          | `~/.claude/skills/python-django/SKILL.md`     |
| Vue.js / Frontend              | `~/.claude/skills/vue-frontend/SKILL.md`      |
| PySpark / Airflow / Hadoop     | `~/.claude/skills/data-engineering/SKILL.md`  |
| C# / Unity Android             | `~/.claude/skills/unity-android/SKILL.md`     |
| GitLab CI/CD (MPRJ)            | `~/.claude/skills/gitlab-ci/SKILL.md`         |
| Infisical (secrets)            | `~/.claude/skills/infisical-secrets/SKILL.md` |
| OpenTelemetry / Dynatrace      | `~/.claude/skills/opentelemetry/SKILL.md`     |
| Documentos Word / .docx        | `/mnt/skills/public/docx/SKILL.md`            |
| PDFs (criar ou extrair)        | `/mnt/skills/public/pdf/SKILL.md`             |
| Apresentações .pptx            | `/mnt/skills/public/pptx/SKILL.md`            |
| Planilhas .xlsx                | `/mnt/skills/public/xlsx/SKILL.md`            |
| UI / Frontend / Componentes    | `/mnt/skills/public/frontend-design/SKILL.md` |
| Arquivos enviados pelo usuário | `/mnt/skills/public/file-reading/SKILL.md`    |
| PDFs para leitura              | `/mnt/skills/public/pdf-reading/SKILL.md`     |

---

## 💻 Ambiente

| Sistema       | Detalhes                                       |
|---------------|------------------------------------------------|
| Windows 11    | Dev local principal — VS Code, Docker Desktop  |
| Linux Arch    | Garuda Linux — terminal, pipelines, servidores |
| Linux Shell   | Fish / Bash                                    |
| Windows Shell | PowerShell + WSL2                              |

- Paths: `pathlib.Path` — nunca concatenação de strings com `/`
- Secrets: sempre via Infisical — nunca `.env` commitado
- Scripts cross-platform: preferir `Makefile` ou Python

---

## 🔌 MCP Servers

| Server       | Uso                                    | Escopo  |
|--------------|----------------------------------------|---------|
| `gitlab`     | MRs, issues, pipelines no MPRJ GitLab  | global  |
| `filesystem` | Acesso estruturado a arquivos          | global  |
| `postgres`   | Queries diretas no banco de dev        | local   |
| `memory`     | Persistência de contexto cross-session | global  |
| `playwright` | Testes E2E                             | project |

---

## 🏛️ Princípios Core

<!-- CACHE_MARKER: principles-stable -->

| Princípio      | Regra                                                            |
|----------------|------------------------------------------------------------------|
| Simplicidade   | Mudança mínima; mínimo de código impactado                       |
| Sem Atalhos    | Causa raiz sempre; `TODO` sem data/responsável é proibido        |
| Impacto Mínimo | Mudanças incrementais e reversíveis                              |
| Sem Gambiarras | Se parece gambiarra → implementar a solução elegante             |
| Autonomia      | Bug report → corrigir direto, sem pedir orientação passo a passo |

```
Composição        > Herança
Protocol/Interface > Classe concreta
Injeção de dep.   > Instanciação direta
Repositório       > Acesso direto ao banco
Config externa    > Hardcode
```

---

## 🔄 Orquestração de Workflow

- Tarefas 3+ etapas → escrever plano em `tasks/todo.md` antes de implementar
- Decisões arquiteturais → registrar em `tasks/decisions.md` (formato ADR)
- Após correção do usuário → atualizar `tasks/lessons.md` imediatamente
- Nunca marcar como concluído sem provar funcionamento

**Subagentes:** usar para contexto isolado, análises paralelas, exploração de código.  
**Agent Teams:** múltiplas subtarefas independentes → rodar em paralelo.

```
Precisa de contexto isolado?
├── SIM → Uma subtarefa?  → Subagente
│         Várias?         → Agent Team paralelo
└── NÃO → Claude principal resolve diretamente
```

---

## ✅ Checklist Universal Pré-Entrega

<!-- CACHE_MARKER: checklist-stable -->

```
[ ] Testes passando — pytest -n auto (ou equivalente da stack)
[ ] Lint sem erros — ruff + mypy (ou build limpa para C#)
[ ] Sem regressões no comportamento existente
[ ] Secrets via Infisical — nada hardcoded
[ ] Cobertura ≥ 80% em código novo
[ ] tasks/lessons.md atualizado se houve correção durante a tarefa
[ ] tasks/decisions.md atualizado se houve decisão arquitetural
[ ] "Um engenheiro sênior aprovaria isso?" → SIM
```

---

## 🔒 Segurança

```json
// NUNCA
{
  "permissions": {
    "allow": [
      "Bash(*)"
    ]
  }
}

// CORRETO
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(uv *)"
    ]
  }
}
```

- Hook `PreToolUse` registra git commit/push em `~/.claude/audit.log`
- Configs sensíveis sempre com `--scope local`

---

## 💡 Prompt Caching (uso via API)

Blocos estáveis para cachear: princípios, checklists, seções de stack das skills.  
Blocos voláteis (não cachear): `tasks/todo.md`, estado atual do código, resultados MCP.

```python
{"type": "text", "text": CONTEUDO_ESTAVEL, "cache_control": {"type": "ephemeral"}}
```

Cache `ephemeral` dura ~5 min. Reenviar o bloco a cada 4 min garante hit contínuo.

---

## 🤖 Headless / CI

```bash
claude -p "revise o MR #42" --output-format json
claude -p "rode testes" --allowedTools "Read,Bash(uv run pytest *)"
tail -200 app.log | claude -p "identifique erros críticos"
```

---

*v3.1 — global: `~/.claude/CLAUDE.md` | projetos sobrescrevem via CLAUDE.md local*
