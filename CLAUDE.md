# CLAUDE.md — Configuração Global Multi-Stack

<!-- CACHE_MARKER: global-v3-stable -->
<!-- Este bloco é estável entre sessões — ideal para Prompt Caching -->
<!-- Idioma: comentários em português | identificadores em inglês -->

> **Versão:** 3.0 | **Cache Marker:** global-v3-2026  
> **Última atualização:** 2026-05-14

---

## ⚡ Bootstrap de Sessão (SEMPRE executar ao iniciar)

```
1. Ler tasks/lessons.md    — absorver padrões e antipadrões aprendidos
2. Ler tasks/todo.md        — retomar contexto da última tarefa ativa
3. Confirmar stack ativa    — carregar seção correspondente abaixo
4. Verificar skills         — carregar skills aplicáveis ao contexto
```

> **Se `tasks/` não existir:** criar estrutura completa antes de qualquer ação.

---

## 🎯 Stacks e Tecnologias

### Stack Principal: Python / Django / Vue.js

- **Python:** 3.12.10
- **Gerenciador de pacotes:** UV (SEMPRE usar `uv` em vez de pip/poetry)
- **Framework Backend:** Django 6.x
- **Framework Frontend:** Vue.js 3 + Vite
- **Banco de Dados:** PostgreSQL 15+
- **Secrets Management:** Infisical
- **Observabilidade:** Dynatrace + OpenTelemetry
- **VCS:** GitLab on-premise (https://gitlab-dti.mprj.mp.br/)
- **CI/CD:** GitLab CI/CD (autenticação via Access Token)

### Stack Dados: PySpark / Airflow / Hadoop

- **Processing:** PySpark 3.x
- **Orquestração:** Apache Airflow
- **Storage:** Hadoop HDFS

### Stack Mobile: C# / Unity (Android)

- **Engine:** Unity 2022.3 LTS
- **Target:** Mobile Android (IL2CPP + ARM64)
- **Renderização:** URP (Universal Render Pipeline)

---

## 🔄 Orquestração de Workflow

### Modo Planejamento — Obrigatório para tarefas 3+ etapas

1. **Escrever plano** em `tasks/todo.md` com checklist detalhado
2. **Validar com usuário** antes de implementar
3. **Implementar** seguindo o plano aprovado
4. **Se algo falhar:** PARAR, replanejar, validar novamente

### Uso de Subagentes

**Quando usar:**
- Exploração profunda de código sem poluir contexto principal
- Tarefas paralelas independentes (análise de múltiplos módulos)
- Investigações isoladas (security review, N+1 queries, etc.)

**Padrão de delegação:**
```
Uma subtarefa isolada     → Subagente simples (Agent tool)
Múltiplas subtarefas      → Agent Team (paralelismo)
Pesquisa sem edição       → Explore agent
```

### Auto-Aperfeiçoamento Contínuo

**Após qualquer correção do usuário:**
1. Atualizar `tasks/lessons.md` imediatamente
2. Categorizar por: `stack | padrão | antipadrão`
3. Incluir contexto: por que falhou, solução correta, quando aplicar

**Revisar `lessons.md` no bootstrap de cada sessão.**

### Decisões Arquiteturais

- Registrar em `tasks/decisions.md` (formato ADR)
- Incluir: contexto, decisão, alternativas consideradas, trade-offs, consequências
- Atualizar status: `Proposto → Aceito → Implementado` ou `Depreciado`

---

## 📁 Estrutura de Tarefas

```
tasks/
├── todo.md        # Plano ativo com checklist (tarefa atual)
├── lessons.md     # Lições aprendidas (categorizadas por stack)
├── decisions.md   # ADRs — Architecture Decision Records
└── archive/       # Tarefas concluídas (mover após conclusão)
```

### Template: `todo.md`

```markdown
# Tarefa: [nome descritivo]

## Objetivo

[Descrição clara + critério de aceite específico]

## Contexto

[Background, motivação, stakeholders]

## Plano

- [ ] Etapa 1: [descrição detalhada]
- [ ] Etapa 2: [descrição detalhada]
- [x] Etapa N: [concluída]

## Verificação

- [ ] Testes passando (pytest -n auto)
- [ ] Lint sem erros (ruff + mypy)
- [ ] Cobertura ≥ 80% em código novo
- [ ] Pre-commit hooks passando
- [ ] Documentação atualizada

## Review

[Resumo do resultado, decisões tomadas, impacto, próximos passos]
```

### Template: `lessons.md`

```markdown
# Lições Aprendidas

## Python / Django

### [PADRÃO] SQLAlchemy engine para Pandas ↔ PostgreSQL

**Contexto:** Evitar UserWarning DBAPI2 ao usar Pandas com Django ORM  
**Solução:** Usar `create_engine()` do SQLAlchemy  
**Quando aplicar:** Sempre que conectar Pandas diretamente ao banco

### [ANTIPADRÃO] N+1 queries sem select_related

**Problema:** Loop sobre queryset sem prefetch causou timeout  
**Solução:** Sempre usar `.select_related()` ou `.prefetch_related()`  
**Detecção:** Django Debug Toolbar, nplusone detector

## PySpark

### [ANTIPADRÃO] .collect() sem amostragem prévia

**Problema:** collect() em dataset de 10M linhas estourou memória do driver  
**Solução:** Sempre `.limit()` ou `.sample()` antes de collect()  
**Quando aplicar:** Qualquer operação que traga dados para driver

## C# / Unity

### [PADRÃO] ScriptableObjects para configuração

**Contexto:** Evitar hardcode e facilitar tweaking de gameplay  
**Solução:** Criar SO para configs de armas, inimigos, níveis  
**Quando aplicar:** Qualquer dado que designers precisam ajustar
```

### Template: `decisions.md`

```markdown
# Architecture Decision Records

## ADR-001: [Título da decisão]

**Status:** Proposto | Aceito | Implementado | Depreciado  
**Data:** 2026-05-14  
**Decisor(es):** [nomes]

### Contexto

[Descrever o problema ou necessidade que motivou a decisão]

### Decisão

[Qual foi a decisão tomada]

### Alternativas Consideradas

1. **Alternativa A:** [descrição] — rejeitada porque [motivo]
2. **Alternativa B:** [descrição] — rejeitada porque [motivo]

### Consequências

**Positivas:**
- [benefício 1]
- [benefício 2]

**Negativas:**
- [trade-off 1]
- [trade-off 2]

**Neutras:**
- [impacto neutro]

### Notas de Implementação

[Detalhes técnicos, links, referências]
```

---

## 🐍 Stack: Python / Django / Vue.js

<!-- @cache: carregar quando stack=python -->

### Princípios Obrigatórios

#### TDD: Red → Green → Refactor (sem exceções)
- Escrever teste que falha ANTES de qualquer código
- Implementar mínimo necessário para passar
- Refatorar mantendo testes verdes

#### Qualidade de Código
- **Lint:** Ruff (check + format) + Mypy (strict mode)
- **Testes:** Pytest ≥ 80% cobertura em código novo
- **Paralelismo:** SEMPRE usar `pytest -n auto` para execução paralela
- **DI:** Protocol-based (não herança concreta)
- **Princípios SOLID:** foco em SRP + DIP

#### Convenções
- **Comentários:** Português (explicar por quê, não o quê)
- **Identificadores:** Inglês (variáveis, funções, classes)
- **Docstrings:** Português, formato Google

### Gerenciamento de Dependências com UV

```bash
# SEMPRE usar uv em vez de pip/poetry
uv pip install <pacote>              # instalar pacote
uv pip install -r requirements.txt   # instalar requirements
uv pip compile pyproject.toml -o requirements.txt  # compilar deps
uv venv                              # criar venv
uv run pytest                        # rodar comando no venv
```

### Legado e Refatoração

**Antes de refatorar código legado:**
1. Escrever **testes de caracterização** (capturar comportamento atual)
2. Executar testes → garantir que passam
3. Refatorar incrementalmente
4. Executar testes após cada mudança
5. Nunca quebrar API pública sem aprovação explícita

**Padrões incrementais preferidos:**
- Chain of Responsibility (pipeline de handlers)
- Repository (abstração de acesso a dados)
- Strategy (algoritmos intercambiáveis)
- Service Layer (lógica de negócio fora de views/models)

### Ciclo de Qualidade (Executar antes de cada commit)

```bash
# Auto-fix e formatação
ruff check . --fix
ruff format .

# Type checking
mypy .

# Testes com cobertura e paralelismo
pytest --cov --cov-report=term-missing -n auto

# Se tudo passar → commit
git add .
git commit -m "feat: descrição da mudança"
```

### Django: Boas Práticas

#### Views
- Apenas orquestração HTTP (request → response)
- Lógica de negócio em Services
- Validação em Serializers (DRF) ou Forms

#### Models
- Apenas dados e validação simples
- Métodos: `save()`, `clean()`, `__str__()`, propriedades calculadas simples
- Lógica complexa → Services

#### Services (padrão obrigatório)
```python
# apps/minha_app/services.py
from typing import Protocol
from .models import User

class UserRepository(Protocol):
    """Interface para acesso a dados de usuários."""
    def get_by_id(self, user_id: int) -> User: ...
    def save(self, user: User) -> User: ...

class UserService:
    """Lógica de negócio de usuários."""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def activate_user(self, user_id: int) -> User:
        """Ativa um usuário e envia email de boas-vindas."""
        user = self.repository.get_by_id(user_id)
        user.is_active = True
        user = self.repository.save(user)
        # Lógica de email aqui
        return user
```

#### Queries e Performance
- **SEMPRE** usar `.select_related()` para ForeignKey
- **SEMPRE** usar `.prefetch_related()` para Many-to-Many
- **NUNCA** queries dentro de loops → detectar com Django Debug Toolbar
- **Índices:** adicionar para campos usados em filters/order_by frequentes

### Vue.js 3: Boas Práticas

#### Composables (Composition API)
```javascript
// composables/useAuth.js
import { ref, computed } from 'vue'

export function useAuth() {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  
  async function login(credentials) {
    // lógica de login
  }
  
  return { user, isAuthenticated, login }
}
```

#### Estrutura de Componentes
- Single File Components (SFC)
- Props validadas com TypeScript ou PropTypes
- Eventos nomeados com kebab-case
- Slots para composição flexível

### Observabilidade: OpenTelemetry + Dynatrace

```python
# Instrumentação automática Django
from opentelemetry.instrumentation.django import DjangoInstrumentor

DjangoInstrumentor().instrument()

# Tracing manual para operações críticas
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_payment(order_id: int):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("order.id", order_id)
        # lógica de pagamento
```

### Secrets: Infisical

```python
# Nunca hardcodear secrets
# settings.py
import os
from infisical import InfisicalClient

client = InfisicalClient(token=os.getenv("INFISICAL_TOKEN"))
secrets = client.get_all_secrets(environment="production")

SECRET_KEY = secrets["SECRET_KEY"]
DATABASE_PASSWORD = secrets["DB_PASSWORD"]
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml — exemplo
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.12
  before_script:
    - pip install uv
    - uv pip install -r requirements.txt
  script:
    - ruff check .
    - mypy .
    - pytest -n auto --cov --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

## 📊 Stack: Engenharia de Dados (PySpark / Airflow / Hadoop)

<!-- @cache: carregar quando stack=dados -->

### Princípios Obrigatórios

#### PySpark
- **NUNCA** `.collect()` sem amostragem prévia em datasets grandes
- **SEMPRE** particionar antes de joins custosos
- **Validar schema** antes de qualquer transformação
- **Broadcast** joins para tabelas pequenas (<200MB)
- **Persist/Cache** datasets reutilizados múltiplas vezes

```python
# ❌ ERRADO
df = spark.read.parquet("hdfs://large_dataset")
results = df.collect()  # BOOM! OOM no driver

# ✅ CORRETO
df = spark.read.parquet("hdfs://large_dataset")
sample = df.limit(100).collect()  # ou .sample(0.01)
```

#### Airflow DAGs
- **Idempotentes** por padrão (múltiplas execuções = mesmo resultado)
- **Validar dados** entrada/saída (schema, contagem, nulls)
- **Alertas** para falhas silenciosas (dados vazios ≠ erro automático)
- **Particionamento** documentado (estratégia + coluna)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'etl_vendas',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # 2h da manhã diariamente
    catchup=False,
    tags=['vendas', 'etl'],
) as dag:
    
    extract = PythonOperator(task_id='extract', python_callable=extract_data)
    transform = PythonOperator(task_id='transform', python_callable=transform_data)
    load = PythonOperator(task_id='load', python_callable=load_data)
    
    extract >> transform >> load
```

### Qualidade de Pipeline

- **Testes:** fixtures sintéticos (NUNCA dados de produção)
- **Logging:** linhas entrada / linhas saída / linhas descartadas por etapa
- **Métricas:** duração, memória, shuffle size
- **Validação:** Great Expectations ou similar

### SQLAlchemy para Pandas ↔ PostgreSQL

```python
from sqlalchemy import create_engine
import pandas as pd

# ✅ CORRETO — evita warnings DBAPI2
engine = create_engine("postgresql://user:pass@host:5432/db")
df = pd.read_sql("SELECT * FROM users", con=engine)
df.to_sql("users_backup", con=engine, if_exists="replace")
```

---

## 🎮 Stack: C# / Unity (Mobile Android)

<!-- @cache: carregar quando stack=unity -->

### Princípios Obrigatórios

#### TDD com Unity Test Framework
- **Edit Mode Tests:** lógica pura, sem MonoBehaviours
- **Play Mode Tests:** interações de gameplay, física, UI

```csharp
// EditMode/PlayerStatsTests.cs
using NUnit.Framework;

public class PlayerStatsTests
{
    [Test]
    public void TakeDamage_ReducesHealth()
    {
        var player = new Player(health: 100);
        player.TakeDamage(30);
        Assert.AreEqual(70, player.Health);
    }
}
```

#### Build Settings
- **Scripting Backend:** IL2CPP (não Mono)
- **Architecture:** ARM64 (obrigatório para Google Play)
- **Rendering:** URP (Universal Render Pipeline)

#### Arquitetura

**❌ EVITAR:**
- Singletons estáticos (dificulta testes)
- `FindObjectOfType` em runtime (lento)
- Lógica em MonoBehaviours gigantes

**✅ PREFERIR:**
- Referências diretas via Inspector
- UnityEvents para comunicação
- ScriptableObjects para configuração
- MVC/MVP para separação de concerns

```csharp
// ScriptableObject para configuração de arma
[CreateAssetMenu(fileName = "WeaponData", menuName = "Gameplay/Weapon")]
public class WeaponData : ScriptableObject
{
    public string weaponName;
    public int damage;
    public float fireRate;
    public AudioClip fireSound;
}
```

#### Performance Mobile

- **Object Pooling** para entidades com spawn frequente
- **Evitar GC allocations** em hot paths (Update, FixedUpdate)
- **Texture atlasing** para reduzir draw calls
- **Occlusion culling** para cenários grandes

### Checklist de Build

```
[ ] Unity Test Framework: Edit Mode passando
[ ] Unity Test Framework: Play Mode passando
[ ] Console sem erros (warnings justificados)
[ ] Profiler: sem alocações GC em hot paths
[ ] Build testada em device físico Android
[ ] Player Settings: IL2CPP + ARM64 + URP
[ ] Tamanho APK/AAB < limite aceitável (ex: 150MB)
[ ] Performance: 60 FPS em device target
```

---

## 🏛️ Princípios Core

<!-- CACHE_MARKER: principles-stable-v3 -->

| Princípio         | Regra                                                                     |
|-------------------|---------------------------------------------------------------------------|
| **Simplicidade**  | Mudança mais simples possível; mínimo de código impactado                 |
| **Causa Raiz**    | Sempre investigar causa raiz; nunca atalhos ou gambiarras                 |
| **TODOs**         | TODO sem data/responsável é proibido; criar issue/task em vez disso       |
| **Impacto**       | Mudanças incrementais e reversíveis; feature flags para alto risco        |
| **Elegância**     | Código simples e claro > inteligente e obscuro                            |
| **Autonomia**     | Bug report → corrigir direto, sem pedir orientação passo a passo          |
| **Testes**        | Nunca marcar tarefa como concluída sem provar funcionamento               |

### Padrões Arquiteturais Preferidos

```
Composição          > Herança
Protocol/Interface  > Classe concreta
Injeção de dep.     > Instanciação direta
Evento/Callback     > Polling ativo
Repositório         > Acesso direto ao banco
Config externa      > Hardcode
Imutabilidade       > Mutação de estado
```

### Verificação Antes de Concluir

**Pergunta obrigatória antes de marcar tarefa como concluída:**

> *"Um engenheiro sênior aprovaria isso?"*

Se a resposta for "não" ou "talvez", investigar e corrigir antes de continuar.

---

## ✅ Checklist Universal Pré-Entrega

```
[ ] Testes passando (unitários + integração relevante)
[ ] Lint sem erros (ruff check . && mypy .)
[ ] Cobertura de testes ≥ 80% em código novo
[ ] Sem regressões no comportamento existente
[ ] Documentação atualizada (docstrings, README se aplicável)
[ ] tasks/lessons.md atualizado se houve correção
[ ] tasks/decisions.md atualizado se houve decisão arquitetural
[ ] Pre-commit hooks passando
[ ] Sem secrets ou credenciais no código
[ ] "Um engenheiro sênior aprovaria?" → SIM
```

---

## 🧠 Skills Disponíveis

**Verificar antes de qualquer tarefa não trivial se existe skill aplicável.**

Skills são expertise automatizada que Claude carrega por contexto. Localizadas em `.claude/skills/`.

| Contexto                              | Skill                              |
|---------------------------------------|------------------------------------|
| Django Service Layer / Repository     | `django-service-layer`             |
| PySpark Pipeline / ETL                | `pyspark-pipeline`                 |
| Unity Mobile / Android                | `unity-mobile`                     |
| GitLab CI/CD                          | `gitlab-cicd`                      |
| OpenTelemetry / Dynatrace             | `opentelemetry-instrumentation`    |
| Infisical Secrets Management          | `infisical-secrets`                |
| PostgreSQL Performance / Indexing     | `postgres-performance`             |
| Vue.js 3 Composition API              | `vuejs-composition`                |

**Regra:** Carregar a skill ANTES de escrever código ou criar arquivos relacionados.

---

## 🔧 Configuração e Automação

### Hooks Configurados

Hooks estão em `.claude/settings.json` e executam automaticamente em eventos específicos.

**Eventos principais:**
- `PostToolUse(Write(*.py))` → auto-format com ruff
- `PostToolUse(Write(**/*))` → executar testes relacionados
- `SessionStart` → mostrar git status + últimos commits
- `PreToolUse(Bash(git commit*))` → verificar secrets

### MCP Servers Configurados

**Model Context Protocol** conecta Claude Code a ferramentas externas.

| Server       | Propósito                           | Escopo    |
|--------------|-------------------------------------|-----------|
| `gitlab`     | PRs, issues, pipelines              | project   |
| `postgres`   | Queries, schema, migrations         | project   |
| `infisical`  | Secrets management                  | local     |
| `dynatrace`  | Métricas, traces, logs              | local     |
| `memory`     | Persistência cross-session          | global    |

**Ver `.claude/settings.json` para detalhes.**

### Comandos Customizados

Comandos em `.claude/commands/` são invocados com `/comando`.

| Comando              | Descrição                                        |
|----------------------|--------------------------------------------------|
| `/review-pr`         | Revisa PR atual (segurança + qualidade + padrões)|
| `/n1-audit`          | Analisa código Django para N+1 queries           |
| `/check-migrations`  | Verifica migrations pendentes e conflitos        |
| `/dynatrace-check`   | Consulta Dynatrace para métricas da aplicação    |

---

## 💡 Prompt Caching — Economia de Tokens

> **Aplicável ao usar Claude via API** (não Claude Code CLI diretamente).

### Blocos Estáveis (cacheable)

Estes blocos raramente mudam e devem ser marcados com `cache_control: {"type": "ephemeral"}`:

- Princípios Core
- Padrões arquiteturais
- Checklists universais
- Formatos de `tasks/`
- Estrutura de Skills
- Configurações de stack

### Blocos Voláteis (não cachear)

Estes mudam frequentemente por sessão:

- Tarefa ativa (`tasks/todo.md`)
- Estado atual do código
- Contexto de erro em investigação
- Diff de mudanças

### Estratégia na API

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-...")

# Bloco estável — cacheia por ~5 minutos
STABLE_CONTENT = open("CLAUDE.md").read()

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": STABLE_CONTENT,
                "cache_control": {"type": "ephemeral"}  # ← CACHEIA
            },
            {
                "type": "text",
                "text": f"Tarefa atual:\n{todo_md}\n\nRequest: {user_input}"
                # ← NÃO cacheia (muda toda chamada)
            }
        ]
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=messages
)
```

### Economia Estimada

| Situação                | Sem cache     | Com cache        | Economia |
|-------------------------|---------------|------------------|----------|
| 10 chamadas/sessão      | 10× tokens    | 1× + 9× hit      | ~80%     |
| CLAUDE.md ~3.500 tokens | 35.000 tokens | ~7.000 tokens    | ~80%     |
| Sessão longa (20 calls) | 70.000 tokens | ~10.500 tokens   | ~85%     |

**Cache `ephemeral` dura ~5 minutos de inatividade.**

Para sessões longas: reenviar bloco estável a cada 4 minutos garante hit contínuo.

---

## 🔒 Segurança e Compliance

### Secrets

```bash
# ❌ NUNCA
KEYCLOAK_SECRET=abc123  # hardcoded
api_key = "sk-proj-123"  # no código

# ✅ SEMPRE
# .env (não commitado)
KEYCLOAK_SECRET=abc123

# settings.py
import os
SECRET_KEY = os.getenv("SECRET_KEY")

# Ou via Infisical (preferido)
from infisical import InfisicalClient
secrets = InfisicalClient().get_all_secrets()
```

### GitLab Access Token

```bash
# .env (local, não commitar)
GITLAB_TOKEN=glpat-xxxxxxxxxxxx

# .claude/settings.json (commitar, mas sem token)
{
  "mcpServers": {
    "gitlab": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gitlab"],
      "env": {
        "GITLAB_TOKEN": "${GITLAB_TOKEN}"  # ← lê do env
      }
    }
  }
}
```

### Permissões em Produção

```json
// ❌ NUNCA em produção
{"permissions": {"allow": ["Bash(*)"]}}

// ✅ Whitelist específica
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(pytest *)",
      "Read(**/*)",
      "Write(src/**/*)",
      "Write(tests/**/*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Write(/etc/*)",
      "Write(~/.ssh/*)"
    ]
  }
}
```

---

## 📚 Comunicação com o Usuário

### Tom e Estilo

- **Resumo de alto nível** antes de mostrar código
- **Destacar trade-offs** quando houver ≥ 2 abordagens válidas
- **Sinalizar riscos** e side effects explicitamente
- **Máximo 2 perguntas** de clarificação por vez
- **Sem emojis** (a menos que usuário solicite)

### Estrutura de Resposta

1. **O que vou fazer** (1 frase)
2. **Executar ações** (tool calls)
3. **Resultado** (1-2 sentenças)

**Evitar:**
- Explicações prolixas antes de agir
- Narração de processo interno
- Summaries repetitivos ("Acabei de fazer X...")

---

## 🚀 Roteiro de Aprendizado

### Semana 1 — Fundação
- [ ] Executar `/init` para gerar CLAUDE.md inicial
- [ ] Criar estrutura `tasks/` com templates
- [ ] Configurar `.claude/settings.json` básico
- [ ] Praticar: refatoração simples + revisar diff

### Semana 2 — Produtividade
- [ ] Criar 3-5 comandos customizados
- [ ] Configurar hooks de auto-format
- [ ] Configurar permissões pré-aprovadas
- [ ] Experimentar `/security-review`

### Semana 3 — Integração
- [ ] Adicionar MCP server GitLab
- [ ] Adicionar MCP server PostgreSQL
- [ ] Criar Skill para Django Service Layer
- [ ] Testar criação de PR via Claude

### Semana 4+ — Automação
- [ ] Configurar GitLab CI com Claude Code
- [ ] Criar Agent Team para revisão paralela
- [ ] Otimizar uso de tokens com caching
- [ ] Contribuir com Skills reutilizáveis

---

## 📖 Referências

- **Claude Code Docs:** https://code.claude.com/docs
- **Claude Code GitHub:** https://github.com/anthropics/claude-code
- **MCP Servers:** https://github.com/modelcontextprotocol/servers
- **Infisical Docs:** https://infisical.com/docs
- **Dynatrace OpenTelemetry:** https://www.dynatrace.com/support/help/extend-dynatrace/opentelemetry
- **GitLab API:** https://docs.gitlab.com/ee/api/

---

*Este arquivo é a "constituição" do projeto. Claude Code lê ele no início de cada sessão.*  
*Mantenha atualizado, conciso, e sem secrets.*  
*Para expertise especializada, use Skills em `.claude/skills/`.*
