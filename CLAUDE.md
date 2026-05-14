# CLAUDE.md — Configuração Global

<!-- CACHE_MARKER: stable-root-v2 -->
<!-- Idioma: comentários em português | identificadores em inglês -->
<!-- Este bloco é estável entre sessões — ideal para Prompt Caching ephemeral -->
<!-- Projetos específicos sobrescrevem seções via CLAUDE.md local na raiz do repo -->

---

## ⚡ Bootstrap de Sessão (executar SEMPRE ao iniciar)

```
1. Ler tasks/lessons.md  — absorver padrões e antipadrões acumulados
2. Ler tasks/todo.md     — retomar contexto da última tarefa ativa
3. Confirmar stack ativa → carregar seção de stack correspondente abaixo
4. Verificar skills disponíveis para o contexto da tarefa
```

> Se `tasks/` não existir: criar estrutura completa antes de qualquer outra ação.

---

## 💻 Ambiente

| Sistema         | Detalhes                                    |
|-----------------|---------------------------------------------|
| Windows 11      | Dev local principal, VS Code, Docker Desktop|
| Linux Arch      | Garuda Linux — terminal, pipelines, servers |
| Shell (Linux)   | Fish / Bash                                 |
| Shell (Windows) | PowerShell + WSL2                           |

### Comandos cross-platform

- Preferir scripts `Makefile` ou scripts Python para compatibilidade entre OS
- Paths: usar `pathlib.Path` (nunca concatenação de strings com `/` hardcoded)
- Variáveis de ambiente: sempre via Infisical — nunca `.env` commitado

---

## 🧠 Skills Disponíveis

Antes de qualquer tarefa não trivial, verificar se existe uma skill aplicável e carregá-la:

| Contexto                        | Skill a carregar                                         |
|---------------------------------|----------------------------------------------------------|
| Python / Django / DRF           | `~/.claude/skills/python-django/SKILL.md`                |
| Vue.js / Frontend               | `~/.claude/skills/vue-frontend/SKILL.md`                 |
| PySpark / Airflow / Hadoop      | `~/.claude/skills/data-engineering/SKILL.md`             |
| C# / Unity Android              | `~/.claude/skills/unity-android/SKILL.md`                |
| GitLab CI/CD (MPRJ)             | `~/.claude/skills/gitlab-ci/SKILL.md`                    |
| Infisical (secrets management)  | `~/.claude/skills/infisical-secrets/SKILL.md`            |
| OpenTelemetry / Dynatrace       | `~/.claude/skills/opentelemetry/SKILL.md`                |
| Documentos Word / .docx         | `/mnt/skills/public/docx/SKILL.md`                       |
| PDFs (criar ou extrair)         | `/mnt/skills/public/pdf/SKILL.md`                        |
| Apresentações .pptx             | `/mnt/skills/public/pptx/SKILL.md`                       |
| Planilhas .xlsx                 | `/mnt/skills/public/xlsx/SKILL.md`                       |
| UI / Frontend / Componentes     | `/mnt/skills/public/frontend-design/SKILL.md`            |
| Arquivos enviados pelo usuário  | `/mnt/skills/public/file-reading/SKILL.md`               |
| PDFs para leitura               | `/mnt/skills/public/pdf-reading/SKILL.md`                |

**Regra:** carregar a skill ANTES de escrever qualquer código ou criar qualquer arquivo.

---

## 🔌 MCP Servers Configurados

Os servidores MCP abaixo estão pré-configurados em `~/.claude/settings.json`.

| Server           | Uso principal                                   | Escopo   |
|------------------|-------------------------------------------------|----------|
| `gitlab`         | PRs, issues, pipelines no MPRJ GitLab           | global   |
| `filesystem`     | Acesso estruturado a arquivos do projeto        | global   |
| `postgres`       | Queries diretas no banco de desenvolvimento     | local    |
| `memory`         | Persistência de contexto cross-session          | global   |
| `playwright`     | Testes E2E automatizados                        | project  |

### Comandos de uso na sessão

```bash
# GitLab MPRJ
"Liste os MRs abertos no repositório X"
"Crie um MR para a branch feature/Y"

# PostgreSQL
"Consulte a tabela users e mostre os 10 últimos registros"
"Verifique índices ausentes na tabela audit_logs"

# Memory
"Salve o contexto desta sessão para amanhã"
```

---

## 🔄 Orquestração de Workflow

### Modo Planejamento — Padrão para tarefas 3+ etapas

1. Escrever plano em `tasks/todo.md`
2. Validar com usuário
3. Só então implementar

Se algo der errado: **PARAR e replanejar** — nunca continuar forçando.  
Decisões arquiteturais: registrar em `tasks/decisions.md` (formato ADR).

### Subagentes — Regras

- Usar liberalmente para manter o contexto principal limpo
- Uma tarefa por subagente; retornar resultados estruturados (não prosa solta)
- Delegar: exploração de código, análises paralelas, validações isoladas, pesquisa

```
Precisa de contexto isolado?
├── SIM → É uma ou várias subtarefas?
│         ├── UMA     → Subagente (Task tool)
│         └── VÁRIAS  → Agent Team paralelo
└── NÃO → Claude principal resolve diretamente
```

### Agent Teams — Paralelismo

```
Coordene 3 agentes em paralelo:
- Agente 1: auditoria de segurança em apps/auth/
- Agente 2: análise de N+1 em apps/api/
- Agente 3: revisão de migrations pendentes
Consolide os resultados em um relatório único.
```

### Auto-Aperfeiçoamento

- Após qualquer correção do usuário → atualizar `tasks/lessons.md` imediatamente
- Categorizar por: `stack | padrão | antipadrão`
- Revisar `lessons.md` no bootstrap de cada sessão

### Verificação Antes de Concluir

Nunca marcar como concluído sem provar funcionamento.

Pergunta obrigatória: *"Um engenheiro sênior aprovaria isso?"*

```bash
# Python/Django
ruff check . --fix && ruff format . && mypy . && pytest --cov --cov-report=term-missing -n auto

# Unity/C#
# Todos os testes Unity Test Framework (Edit Mode + Play Mode) passando
```

---

## 📁 Estrutura de Tarefas

```
tasks/
├── todo.md        # Plano ativo com checklist
├── lessons.md     # Lições aprendidas (categorizadas por stack)
├── decisions.md   # ADRs — Architecture Decision Records
└── archive/       # Tarefas concluídas (mover via git mv)
```

### `todo.md` — Template

```markdown
# Tarefa: [nome]

## Objetivo
[descrição + critério de aceite]

## Plano
- [ ] Etapa 1
- [x] Etapa 2 (concluída)

## Verificação
- [ ] Testes passando
- [ ] Lint sem erros
- [ ] Checklist pré-entrega

## Review
[resumo, decisões, impacto]
```

### `lessons.md` — Template

```markdown
# Lições Aprendidas

## Python / Django
- [PADRÃO] Usar SQLAlchemy engine para Pandas ↔ banco (evita UserWarning DBAPI2)

## PySpark
- [ANTIPADRÃO] .collect() sem amostragem prévia → estoura memória do driver

## C# / Unity
- [PADRÃO] Evitar singletons estáticos → preferir referências diretas ou UnityEvents
```

### `decisions.md` — Formato ADR

```markdown
# ADR-001: [título]

**Status**: Proposto | Aceito | Depreciado
**Data**: YYYY-MM-DD

## Contexto
## Decisão
## Consequências
```

---

## 🐍 Stack: Python / Django

<!-- CACHE_MARKER: python-stack-stable -->

**Versões:** Python 3.12.10 | Django 6.x | PostgreSQL

### Gerenciador de pacotes: UV (sempre)

```bash
uv init                         # novo projeto
uv add django psycopg2-binary   # adicionar dependências
uv run python manage.py migrate # executar com contexto do venv
uv run pytest -n auto           # rodar testes
uv sync                         # sincronizar dependências
```

> **Nunca** usar `pip install` diretamente — sempre `uv add` ou `uv run`.

### Obrigatório

- **TDD**: Red → Green → Refactor (sem exceções)
- **Lint**: `Ruff` + `mypy` | Testes: `Pytest` com `-n auto` SEMPRE | ≥ 80% cobertura em código novo
- **DI** via `Protocol` (não herança concreta) | Princípios SOLID (SRP + DIP em foco)
- **Comentários**: português | **Identificadores**: inglês
- **Secrets**: Infisical (nunca hardcode, nunca `.env` commitado)

### Legado

- Escrever testes de caracterização **antes** de refatorar
- Padrões incrementais: Chain of Responsibility, Repository, Strategy
- Nunca quebrar API pública sem aprovação explícita
- Commits atômicos e rastreáveis

### Ciclo de Qualidade

```bash
ruff check . --fix && ruff format .
mypy .
pytest --cov --cov-report=term-missing -n auto
```

### Infisical — Gestão de Secrets

```python
from infisical_sdk import InfisicalClient

client = InfisicalClient(token=os.environ["INFISICAL_TOKEN"])
secret = client.secrets.get(secret_name="DATABASE_URL", environment="dev")
```

- Nunca commitar secrets, tokens ou senhas
- Usar Infisical CLI em desenvolvimento: `infisical run -- python manage.py runserver`
- Secrets em CI/CD: injetar via Infisical Machine Identity

### Observabilidade: Dynatrace + OpenTelemetry

- Toda API e task crítica deve ter spans OpenTelemetry
- Usar `opentelemetry-instrument` como wrapper em produção
- Dynatrace consome traces via OTLP exporter
- Ver skill: `~/.claude/skills/opentelemetry/SKILL.md`

### Estrutura de Projeto Django

```
apps/
  minha_app/
    models.py         # apenas dados e validação simples
    services.py       # lógica de negócio
    repositories.py   # acesso a dados (Protocol-based)
    views.py          # orquestração HTTP apenas
    serializers.py    # validação de input/output
    tasks.py          # Celery tasks
    tests/
      test_services.py
      test_views.py
```

### Convenções de Commit

```
feat(scope): descrição curta
fix(scope): descrição curta
refactor(scope): descrição curta
test(scope): descrição curta
chore(scope): descrição curta
```

---

## 🌐 Stack: Frontend (Vue.js)

### Obrigatório

- Vue 3 com Composition API (nunca Options API em código novo)
- TypeScript obrigatório em todos os componentes
- Vite como bundler
- Pinia para gerenciamento de estado
- Vitest para testes unitários de componentes

### Estrutura de Componente

```typescript
// Sempre <script setup lang="ts"> — sem defineComponent()
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  userId: number
}

const props = defineProps<Props>()
const isLoading = ref(false)
</script>
```

### Qualidade

```bash
npm run type-check   # vue-tsc
npm run lint         # eslint
npm run test:unit    # vitest
npm run build        # checar build sem erros
```

---

## 📊 Stack: Engenharia de Dados (PySpark / Airflow / Hadoop)

<!-- CACHE_MARKER: data-stack-stable -->

### Obrigatório

- **Nunca** `.collect()` sem amostragem prévia em datasets grandes
- Particionar antes de joins custosos
- DAGs Airflow: idempotentes por padrão
- Validar schema antes de qualquer transformação
- SQLAlchemy engine para Pandas ↔ banco

### Qualidade de Pipeline

- Testes com fixtures (nunca dados de produção)
- Log obrigatório: linhas entrada / saída / descartadas por etapa
- Alertas para falhas silenciosas (dados vazios ≠ erro automático)
- Particionamento de saída documentado junto com a DAG

### Antipadrões PySpark

```python
# NUNCA — estoura memória do driver
df.collect()

# NUNCA — sem cache em DAGs multi-etapa
df.count()  # recalcula toda a cadeia

# CORRETO — amostragem antes de collect
df.sample(fraction=0.01).collect()
```

---

## 🎮 Stack: C# / Unity (Mobile Android)

<!-- CACHE_MARKER: unity-stack-stable -->

### Obrigatório

- TDD: Red → Green → Refactor com Unity Test Framework
- Build: IL2CPP + ARM64 | Renderização: URP
- Sem singletons estáticos → referências diretas ou UnityEvents
- ScriptableObjects para configuração (zero hardcode)
- Separar lógica de jogo da apresentação (MVC/MVP)
- Object Pooling para entidades com spawn frequente
- Sem `FindObjectOfType` em runtime → injeção via Inspector

### Checklist de Build

```
[ ] Unity Test Framework: Edit Mode + Play Mode passando
[ ] Console sem erros (warnings revisados e justificados)
[ ] Profiler: sem alocações GC em hot paths críticos
[ ] Build testada em device físico Android
[ ] IL2CPP + ARM64 no Player Settings
[ ] Tamanho APK/AAB dentro do limite aceitável
```

---

## 🦊 GitLab — MPRJ On-Premise

**Instância:** `https://gitlab-dti.mprj.mp.br/`  
**Autenticação:** Access Token (Personal ou Project)

### Configuração do MCP GitLab

```bash
# Configurar variável de ambiente (nunca commitar o token)
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_URL="https://gitlab-dti.mprj.mp.br"

# Adicionar MCP server para GitLab on-premise
claude mcp add --scope local gitlab -- npx -y @modelcontextprotocol/server-gitlab \
  --gitlab-url "$GITLAB_URL" \
  --token "$GITLAB_TOKEN"
```

### Operações comuns via MCP

```
"Liste os MRs abertos no grupo backend"
"Crie um MR da branch feature/X para develop com o template padrão"
"Mostre os pipelines falhando no projeto gatekeeper"
"Adicione um comentário de revisão no MR #42"
```

### CI/CD — Estrutura padrão `.gitlab-ci.yml`

```yaml
stages:
  - quality
  - test
  - build
  - deploy

variables:
  UV_SYSTEM_PYTHON: "1"

quality:
  stage: quality
  script:
    - uv run ruff check . --fix
    - uv run mypy .

test:
  stage: test
  script:
    - uv run pytest --cov --cov-report=xml -n auto
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

---

## 🏛️ Princípios Core

<!-- CACHE_MARKER: principles-stable -->

| Princípio      | Regra                                                              |
|----------------|--------------------------------------------------------------------|
| Simplicidade   | Mudança mais simples possível; mínimo de código impactado          |
| Sem Atalhos    | Causa raiz sempre; `TODO` sem data/responsável é proibido          |
| Impacto Mínimo | Mudanças incrementais e reversíveis; feature flags para alto risco |
| Sem Gambiarras | Se parece gambiarra → implementar a solução elegante               |
| Elegância      | Simples e claro > inteligente e obscuro                            |
| Autonomia      | Bug report → corrigir direto, sem pedir orientação passo a passo   |

### Padrões Arquiteturais Preferidos

```
Composição        > Herança
Protocol/Interface > Classe concreta
Injeção de dep.   > Instanciação direta
Evento/Callback   > Polling ativo
Repositório       > Acesso direto ao banco
Config externa    > Hardcode
```

### Comunicação com o Usuário

- Resumo de alto nível antes de mostrar código
- Destacar trade-offs quando houver ≥ 2 abordagens válidas
- Sinalizar riscos e side effects explicitamente
- Máximo 2 perguntas de clarificação por vez

---

## ✅ Checklist Universal Pré-Entrega

<!-- CACHE_MARKER: checklist-stable -->

```
[ ] Testes passando — pytest -n auto (unitários + integração relevante)
[ ] Lint sem erros — ruff check + mypy (ou build limpa para C#)
[ ] Sem regressões no comportamento existente
[ ] Secrets via Infisical — nada hardcoded ou commitado
[ ] Cobertura ≥ 80% em código novo
[ ] Documentação atualizada (docstrings em inglês, comentários em português)
[ ] tasks/lessons.md atualizado se houve correção durante a tarefa
[ ] tasks/decisions.md atualizado se houve decisão arquitetural
[ ] "Um engenheiro sênior aprovaria isso?" → SIM
```

---

## 🔒 Segurança e Boas Práticas

### Permissões — Regra de ouro

```json
// NUNCA
{ "permissions": { "allow": ["Bash(*)"] } }

// CORRETO — sempre específico
{ "permissions": { "allow": ["Bash(git *)", "Bash(pytest *)"] } }
```

### Secrets e Credenciais

```bash
# NUNCA em CLAUDE.md, .env commitado ou no chat
GITLAB_TOKEN=glpat-xxxxx

# CORRETO — variável de ambiente + Infisical
"env": { "GITLAB_TOKEN": "${GITLAB_TOKEN}" }
```

### Auditoria em Ambiente Corporativo (MPRJ)

- Hook `PreToolUse` registra todos os comandos Bash em `~/.claude/audit.log`
- Configs sensíveis sempre com `--scope local` (não commitadas)
- Revisar diff antes de aceitar qualquer mudança em arquivo crítico

---

## 💡 Prompt Caching — Guia de Uso

> Aplicável ao usar Claude via API (não Claude Code CLI diretamente).

### Blocos estáveis (cacheable — marcados com `CACHE_MARKER`)

- Princípios Core
- Padrões arquiteturais
- Checklists universais
- Formatos de `tasks/`
- Seções de stack (python-stack-stable, data-stack-stable, etc.)

### Blocos voláteis (não cachear — mudam por sessão)

- Tarefa ativa (`tasks/todo.md`)
- Estado atual do código
- Contexto de erro em investigação
- Resultados de ferramentas MCP

### Estratégia recomendada na API

```python
import anthropic

client = anthropic.Anthropic()

messages = [
    {
        "role": "user",
        "content": [
            {
                # Bloco estável: envia 1x e cacheia nas chamadas seguintes
                "type": "text",
                "text": CLAUDE_MD_STABLE_CONTENT,
                "cache_control": {"type": "ephemeral"}
            },
            {
                # Bloco volátil: contexto da sessão atual
                "type": "text",
                "text": f"Tarefa atual:\n{todo_md_content}\n\nSolicitação: {user_request}"
            }
        ]
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8096,
    messages=messages
)
```

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

---

## 🤖 Modo Headless / CI

```bash
# Executa tarefa e sai
claude -p "revise o MR #42 e retorne relatório JSON" --output-format json

# Restringir ferramentas em CI
claude -p "rode testes e relate falhas" --allowedTools "Read,Bash(uv run pytest *)"

# Pipe de logs
tail -200 app.log | claude -p "identifique anomalias e erros críticos"

# Arquivos modificados
git diff main --name-only | claude -p "revise estes arquivos para vulnerabilidades"
```

---

*Versão: 3.0 | Cache marker: stable-root-v2*  
*Global: `~/.claude/CLAUDE.md` | Projetos específicos sobrescrevem via CLAUDE.md local.*
