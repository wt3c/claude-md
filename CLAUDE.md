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

**Regra:** carregar a skill ANTES de escrever qualquer código ou criar qualquer arquivo.

---

## 💻 Ambiente

| Sistema       | Detalhes                                       |
|---------------|------------------------------------------------|
| Windows 11    | Dev local principal — Pycharm, Docker Desktop  |
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
| `gitlab`     | MRs, issues, pipelines no MPRJ GitLab  | user    |
| `filesystem` | Acesso estruturado a arquivos          | user    |
| `postgres`   | Queries diretas no banco de dev        | user    |
| `memory`     | Persistência de contexto cross-session | user    |
| `postman`    | Collections, environments, APIs        | user    |
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
| Elegância      | Simples e claro > inteligente e obscuro                          |
| Autonomia      | Bug report → corrigir direto, sem pedir orientação passo a passo |

### Padrões Arquiteturais Preferidos

```
Composição        > Herança
Protocol/Interface > Classe concreta
Injeção de dep.   > Instanciação direta
Repositório       > Acesso direto ao banco
Config externa    > Hardcode
```

---

### Comunicação com o Usuário

- Resumo de alto nível antes de mostrar código
- Destacar trade-offs quando houver ≥ 2 abordagens válidas
- Sinalizar riscos e side effects explicitamente
- Máximo 2 perguntas de clarificação por vez

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
---

## 🎓 Conceitos em Estudo Ativo

<!-- Incluir nos exemplos sempre que relevante e natural -->

### Python: Dataclasses

- Módulo: `dataclasses`
- Usar para: DTOs, Value Objects, modelos de dados, fakes de teste
- Sempre preferir a `dict` solto quando o dado tem estrutura definida

```python
from dataclasses import dataclass, field


@dataclass
class Usuario:
    id: int
    username: str
    email: str
    grupos: list[str] = field(default_factory=list)
```

### Python: Structural Typing com Protocol

- Módulo: `typing`
- Categoria: **Structural Typing** (não Duck Typing — Duck Typing é runtime, Protocol é estático)
- Usar para: contratos/interfaces, injeção de dependência, fakes testáveis
- Classe não precisa herdar — basta ter os métodos do contrato

```python
from typing import Protocol
from dataclasses import dataclass


# Contrato (Structural Typing)
class RepositorioProtocol(Protocol):
    def buscar(self, id: int) -> "Usuario": ...

    def salvar(self, usuario: "Usuario") -> None: ...


# Dado (Dataclass)
@dataclass
class Usuario:
    id: int
    username: str
    email: str


# Fake para teste — satisfaz Protocol sem herdar nada
class FakeRepositorio:
    def __init__(self):
        self._db: list[Usuario] = []

    def buscar(self, id: int) -> Usuario:
        return next(u for u in self._db if u.id == id)

    def salvar(self, usuario: Usuario) -> None:
        self._db.append(usuario)
```

> **Regra:** `@dataclass` = o que o objeto **carrega** | `Protocol` = o que o objeto **sabe fazer**

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

---

### Auditoria em Ambiente Corporativo (MPRJ)

- Hook `PreToolUse` registra todos os comandos Bash em `~/.claude/audit.log`
- Configs sensíveis sempre com `--scope local` (não commitadas)
- Revisar diff antes de aceitar qualquer mudança em arquivo crítico

---

## 💡 Prompt Caching (uso via API)

Blocos estáveis para cachear: princípios, checklists, seções de stack das skills.  
Blocos voláteis (não cachear): `tasks/todo.md`, estado atual do código, resultados MCP.

```python
{"type": "text", "text": CONTEUDO_ESTAVEL, "cache_control": {"type": "ephemeral"}}
```

Cache `ephemeral` dura ~5 min. Reenviar o bloco a cada 4 min garante hit contínuo.

---

### Economia estimada com caching

| Situação                | Sem cache     | Com cache     | Economia |
|-------------------------|---------------|---------------|----------|
| 10 chamadas / sessão    | 10× tokens    | 1× + 9× hit   | ~75–90%  |
| CLAUDE.md ~2.000 tokens | 20.000 tokens | ~3.800 tokens | ~81%     |
| CLAUDE.md ~4.000 tokens | 40.000 tokens | ~6.200 tokens | ~84%     |

> Cache `ephemeral` dura ~5 minutos de inatividade na API Anthropic.  
> Para sessões longas: reenviar o bloco estável a cada 4 minutos garante hit contínuo.

### Gestão de Contexto na Sessão

```
/compact    # Comprime histórico em resumo (IRREVERSÍVEL — salve contexto crítico antes)
/clear      # Limpa tudo — começa fresh
/branch     # Bifurca sessão para explorar sem poluir o principal
/usage      # Dashboard: consumo, custo, rate limits em tempo real
```

**Boas práticas de custo:**

- Usar `/compact` em sessões longas antes que contexto estoure
- Subagentes para exploração — não traz todo o código pro contexto principal
- `--allowedTools` restrito em tarefas simples e headless

## 🤖 Headless / CI

```bash
claude -p "revise o MR #42" --output-format json
claude -p "rode testes" --allowedTools "Read,Bash(uv run pytest *)"
tail -200 app.log | claude -p "identifique erros críticos"
```

---

*v3.1 — global: `~/.claude/CLAUDE.md` | projetos sobrescrevem via CLAUDE.md local*
