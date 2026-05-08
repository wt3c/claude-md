# CLAUDE.md — Contexto Multi-Stack

<!-- CACHE_MARKER: stable-root-v1 -->
<!-- Este bloco é estável entre sessões — ideal para Prompt Caching.         -->
<!-- Projetos específicos sobrescrevem seções via CLAUDE.md local.           -->
<!-- Idioma: comentários em português | identificadores em inglês            -->

---

## ⚡ Bootstrap de Sessão (executar SEMPRE ao iniciar)

```
1. Ler tasks/lessons.md — absorver padrões e antipadrões do projeto
2. Ler tasks/todo.md    — retomar contexto da última tarefa ativa
3. Confirmar stack ativa e carregar seção de stack correspondente (abaixo)
```

> Se `tasks/` não existir: criar estrutura antes de qualquer outra ação.

---

## 🧠 Skills Disponíveis

Antes de qualquer tarefa não trivial, verificar se existe uma skill aplicável:

| Contexto                       | Skill a carregar                              |
|--------------------------------|-----------------------------------------------|
| Documentos Word / .docx        | `/mnt/skills/public/docx/SKILL.md`            |
| PDFs (criar ou extrair)        | `/mnt/skills/public/pdf/SKILL.md`             |
| Apresentações .pptx            | `/mnt/skills/public/pptx/SKILL.md`            |
| Planilhas .xlsx                | `/mnt/skills/public/xlsx/SKILL.md`            |
| UI / Frontend / Componentes    | `/mnt/skills/public/frontend-design/SKILL.md` |
| Arquivos enviados pelo usuário | `/mnt/skills/public/file-reading/SKILL.md`    |
| PDFs para leitura              | `/mnt/skills/public/pdf-reading/SKILL.md`     |

**Regra:** carregar a skill antes de escrever qualquer código ou criar qualquer arquivo.

---

## 🔄 Orquestração de Workflow

### Modo Planejamento — Padrão para tarefas 3+ etapas

- Escrever plano em `tasks/todo.md` → validar com usuário → só então implementar
- Se algo der errado: PARAR e replanejar — nunca continuar forçando
- Decisões arquiteturais: registrar trade-offs em `tasks/decisions.md` (formato ADR)

### Subagentes

- Usar liberalmente para manter contexto principal limpo
- Uma tarefa por subagente; retornar resultados estruturados (não prosa solta)
- Delegar: pesquisa, exploração, análises paralelas, validações isoladas

### Auto-Aperfeiçoamento

- Após qualquer correção do usuário → atualizar `tasks/lessons.md` imediatamente
- Categorizar por: `stack | padrão | antipadrão`
- Revisar `lessons.md` no bootstrap de cada sessão

### Verificação Antes de Concluir

- Nunca marcar como concluído sem provar funcionamento
- Pergunta obrigatória: *"Um engenheiro sênior aprovaria isso?"*
- Python: `ruff check . --fix && ruff format . && mypy . && pytest --cov -n auto`
- Unity/C#: todos os testes Unity Test Framework (Edit Mode + Play Mode) passando

---

## 📁 Estrutura de Tarefas

```
tasks/
├── todo.md        # Plano ativo com checklist
├── lessons.md     # Lições aprendidas (categorizadas por stack)
├── decisions.md   # ADRs — Architecture Decision Records
└── archive/       # Tarefas concluídas
```

### `todo.md`

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

### `lessons.md`

```markdown
# Lições Aprendidas

## Python / Django

- [PADRÃO] Usar SQLAlchemy engine para Pandas ↔ banco (evita UserWarning DBAPI2)

## PySpark

- [ANTIPADRÃO] .collect() sem amostragem prévia → estoura memória do driver

## C# / Unity

- [PADRÃO] Evitar singletons estáticos → preferir referências diretas ou UnityEvents
```

### `decisions.md` (ADR)

```markdown
# ADR-001: [título]

**Status**: Proposto | Aceito | Depreciado  
**Data**: YYYY-MM-DD

## Contexto / Decisão / Consequências
```

---

## 🐍 Stack: Python / Django

<!-- @cache: carregar apenas quando stack=python -->

### Obrigatório

- TDD: Red → Green → Refactor (sem exceções)
- Lint: `Ruff` + `mypy` | Testes: `Pytest` ≥ 80% cobertura em código novo
- DI via `Protocol` (não herança concreta) | Princípios SOLID (SRP + DIP em foco)
- Comentários: português | Identificadores: inglês

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

---

## 📊 Stack: Engenharia de Dados (PySpark / Airflow / Hadoop)

<!-- @cache: carregar apenas quando stack=dados -->

### Obrigatório

- Nunca `.collect()` sem amostragem prévia em datasets grandes
- Particionar antes de joins custosos
- DAGs Airflow: idempotentes por padrão
- Validar schema antes de qualquer transformação
- SQLAlchemy engine para Pandas ↔ banco

### Qualidade de Pipeline

- Testes com fixtures (nunca dados de produção)
- Log obrigatório: linhas entrada / saída / descartadas por etapa
- Alertas para falhas silenciosas (dados vazios ≠ erro automático)
- Particionamento de saída documentado junto com a DAG

---

## 🎮 Stack: C# / Unity (Mobile Android)

<!-- @cache: carregar apenas quando stack=unity -->

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
Composição       > Herança
Protocol/Interface > Classe concreta
Injeção de dep.  > Instanciação direta
Evento/Callback  > Polling ativo
Repositório      > Acesso direto ao banco
Config externa   > Hardcode
```

### Comunicação com o Usuário

- Resumo de alto nível antes de mostrar código
- Destacar trade-offs quando houver ≥ 2 abordagens válidas
- Sinalizar riscos e side effects explicitamente
- Máximo 2 perguntas de clarificação por vez

---

## ✅ Checklist Universal Pré-Entrega

```
[ ] Testes passando (unitários + integração relevante)
[ ] Lint sem erros (Ruff/mypy para Python; build limpa para C#)
[ ] Sem regressões no comportamento existente
[ ] Documentação atualizada (docstrings, comentários, README se aplicável)
[ ] tasks/lessons.md atualizado se houve correção durante a tarefa
[ ] tasks/decisions.md atualizado se houve decisão arquitetural
[ ] "Um engenheiro sênior aprovaria isso?" → SIM
```

---

## 💡 Prompt Caching — Guia de Uso

> Aplicável ao usar Claude via API (não Claude Code CLI diretamente).

### Blocos estáveis (cacheable — marcados com `CACHE_MARKER`)

- Princípios Core
- Padrões arquiteturais
- Checklists universais
- Formatos de `tasks/`

### Blocos voláteis (não cachear — mudam por sessão)

- Tarefa ativa (`tasks/todo.md`)
- Estado atual do código
- Contexto de erro em investigação

### Estratégia recomendada na API

```python
messages = [
    {
        "role": "user",
        "content": [
            {
                # Bloco estável: envia 1x e caches nas chamadas seguintes
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
```

### Economia estimada com caching

| Situação                | Sem cache     | Com cache     | Economia |
|-------------------------|---------------|---------------|----------|
| 10 chamadas / sessão    | 10× tokens    | 1× + 9× hit   | ~75–90%  |
| CLAUDE.md ~2.000 tokens | 20.000 tokens | ~3.800 tokens | ~81%     |

> Cache `ephemeral` dura ~5 minutos de inatividade na API Anthropic.
> Para sessões longas: reenviar o bloco estável a cada 4 minutos garante hit contínuo.

---

*Versão: 2.0 | Cache marker: stable-root-v1*  
*Projetos específicos sobrescrevem seções via CLAUDE.md local na raiz do repo.*
