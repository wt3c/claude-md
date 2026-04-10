# CLAUDE.md — Contexto de Desenvolvimento Multi-Stack

> Arquivo de contexto genérico para Claude Code.
> Projetos específicos devem sobrescrever seções relevantes com seu próprio CLAUDE.md local.
> Convenção de idioma: comentários no código em **português** | identificadores (variáveis, funções, classes) em **inglês**

---

## Orquestração de Workflow

### 1. Modo Planejamento (Plan Mode) — Padrão

- Entrar em modo planejamento para QUALQUER tarefa não trivial (3+ etapas ou decisões arquiteturais)
- Se algo der errado, PARAR imediatamente e replanejar — não continuar forçando
- Usar modo planejamento também nas etapas de verificação, não só na construção
- Escrever especificações detalhadas antes de começar para reduzir ambiguidade
- Para decisões arquiteturais, registrar os trade-offs considerados em `tasks/decisions.md`

### 2. Estratégia de Subagentes

- Usar subagentes liberalmente para manter o contexto principal limpo
- Delegar pesquisa, exploração e análises paralelas a subagentes
- Para problemas complexos, aumentar o compute via subagentes
- Uma tarefa por subagente para execução focada
- Subagentes devem retornar resultados estruturados, não prosa solta

### 3. Loop de Auto-Aperfeiçoamento

- Após QUALQUER correção do usuário: atualizar `tasks/lessons.md` com o padrão identificado
- Escrever regras que previnam o mesmo erro no futuro
- Iterar sem piedade até a taxa de erro cair
- Revisar `lessons.md` no início de cada sessão para projetos relevantes
- Categorizar lições por: stack, padrão arquitetural, antipadrão

### 4. Verificação Antes de Concluir

- Nunca marcar tarefa como concluída sem provar que funciona
- Fazer diff de comportamento entre `main` e suas mudanças quando relevante
- Perguntar a si mesmo: "Um engenheiro sênior aprovaria isso?"
- Executar testes, verificar logs, demonstrar corretude
- Para Python: rodar `Ruff + mypy + Pytest` antes de marcar como feito
- Para Unity/C#: rodar todos os testes do Unity Test Framework (Edit Mode + Play Mode)

### 5. Exigir Elegância (com Equilíbrio)

- Para mudanças não triviais: pausar e perguntar "existe uma forma mais elegante?"
- Se uma correção parecer gambiarra: "Sabendo tudo que sei agora, implementar a solução elegante"
- Pular isso para correções simples e óbvias — não over-engenheirar
- Desafiar o próprio trabalho antes de apresentar
- Elegância ≠ complexidade; código simples e claro é elegante

### 6. Correção Autônoma de Bugs

- Ao receber um bug report: corrigir diretamente, sem pedir orientação passo a passo
- Apontar logs, erros e testes falhando — e resolver
- Zero troca de contexto desnecessária para o usuário
- Corrigir testes de CI falhando sem precisar ser instruído

---

## Gestão de Tarefas

### Ciclo de Vida de uma Tarefa

1. **Planejar Primeiro**: Escrever plano em `tasks/todo.md` com itens checkáveis
2. **Validar o Plano**: Confirmar com o usuário antes de iniciar a implementação
3. **Rastrear Progresso**: Marcar itens como concluídos conforme avança
4. **Explicar Mudanças**: Resumo de alto nível em cada etapa
5. **Documentar Resultados**: Adicionar seção de review ao `tasks/todo.md`
6. **Capturar Lições**: Atualizar `tasks/lessons.md` após correções

### Estrutura de Arquivos de Tarefa

```
tasks/
├── todo.md          # Plano ativo com checklist
├── lessons.md       # Lições aprendidas por categoria de stack
├── decisions.md     # ADRs — Architecture Decision Records
└── archive/         # Tarefas concluídas (mover após review)
```

### Formato do `todo.md`

```markdown
# Tarefa: [nome]

## Objetivo
[descrição clara do que precisa ser feito e o critério de aceite]

## Plano
- [ ] Etapa 1
- [ ] Etapa 2
- [x] Etapa 3 (concluída)

## Verificação
- [ ] Testes passando
- [ ] Lint sem erros
- [ ] Code review checklist

## Review
[resumo do que foi feito, decisões tomadas e impacto]
```

### Formato do `lessons.md`

```markdown
# Lições Aprendidas

## Python / Django
- [PADRÃO] Sempre usar SQLAlchemy engine em vez de conexão DBAPI2 direta com pandas
  Motivo: evita UserWarning e é mais robusto para produção

## PySpark / Dados
- [ANTIPADRÃO] Nunca usar .collect() em DataFrames grandes sem amostragem prévia
  Motivo: estoura memória do driver em datasets de produção

## C# / Unity
- [PADRÃO] Evitar singletons estáticos; preferir referências diretas ou UnityEvents
  Motivo: dificulta testes e cria acoplamento implícito entre sistemas
```

### Formato do `decisions.md` (ADR)

```markdown
# ADR-001: [título da decisão]

**Status**: Aceito | Proposto | Depreciado
**Data**: YYYY-MM-DD

## Contexto
[por que esta decisão foi necessária]

## Decisão
[o que foi decidido]

## Consequências
[trade-offs, dívida técnica intencional, próximos passos]
```

---

## Contextos de Stack

### Python / Django — Projetos Novos e Legados

#### Padrões Obrigatórios

- TDD: Red → Green → Refactor — sem exceções
- Lint: Ruff (formato e lint) + mypy (tipagem estática)
- Testes: Pytest com cobertura mínima de 80% em código novo
- Comentários no código: sempre em português
- Injeção de dependência via Protocol interfaces (não herança concreta)
- Princípios SOLID — especialmente SRP e DIP

#### Refatoração de Legado

- Antes de refatorar: escrever testes de caracterização primeiro
- Aplicar padrões incrementalmente: Chain of Responsibility, Repository, Strategy
- Não quebrar a API pública existente sem aprovação explícita
- Manter changelog de breaking changes em `tasks/decisions.md`
- Preferir refatoração em pequenos passos rastreáveis (commits atômicos)

#### Ciclo de Qualidade

```bash
# Executar antes de marcar qualquer tarefa como concluída
ruff check . --fix && ruff format .
mypy .
pytest --cov --cov-report=term-missing
```

---

### Engenharia de Dados — PySpark / Airflow / Hadoop / Lakehouse

#### Padrões Obrigatórios

- Nunca usar `.collect()` sem amostragem prévia em datasets grandes
- Particionar DataFrames por colunas adequadas antes de joins custosos
- DAGs do Airflow: idempotentes por padrão (reexecutáveis sem efeitos colaterais)
- Documentar lineage de dados em comentários de pipeline
- Usar SQLAlchemy engine para conexões Pandas ↔ banco de dados (evita UserWarning)
- Validar schema antes de qualquer transformação

#### Qualidade de Pipeline

- Testes de pipeline com datasets de fixture (nunca dados de produção)
- Log de métricas obrigatório: linhas entrada / saída / descartadas por etapa
- Alertas em DAGs para falhas silenciosas (dados vazios não são necessariamente erro)
- Particionamento de saída documentado junto com a DAG

---

### C# / Unity — Mobile Game Development (Android)

#### Padrões Obrigatórios

- TDD com Unity Test Framework (Edit Mode + Play Mode)
- Ciclo: Red → Green → Refactor — obrigatório
- Comentários no código: português
- EVITAR singletons estáticos; usar referências diretas ou UnityEvents
- Build: IL2CPP backend + ARM64
- Renderização: URP (Universal Render Pipeline)

#### Arquitetura de Game

- ScriptableObjects para dados de configuração (não hardcode de valores)
- Separar lógica de jogo da apresentação (padrão MVC/MVP)
- Object Pooling para entidades com spawn frequente
- Evitar `FindObjectOfType` em runtime — usar injeção via Inspector
- Assets gerados por IA (Meshy.ai, Suno, ElevenLabs): manter crédito no projeto

#### Checklist Antes de Build

```
[ ] Todos os testes Unity Test Framework passando
[ ] Console sem erros (warnings revisados e justificados)
[ ] Profiler: verificar alocações GC em hot paths críticos
[ ] Build testada em device físico Android
[ ] IL2CPP + ARM64 configurado no Player Settings
[ ] Tamanho do APK/AAB dentro do limite aceitável
```

---

## Princípios Core

### Simplicidade Primeiro

- Fazer cada mudança da forma mais simples possível
- Impactar o mínimo de código necessário
- Código legível por um desenvolvedor júnior é mais valioso que código "inteligente"
- Se precisar de um comentário para explicar **o que** faz (não por quê), considere renomear

### Sem Preguiça (No Laziness)

- Encontrar a causa raiz — nunca correções temporárias sem rastreamento
- Padrão de desenvolvedor sênior em toda entrega
- Nunca deixar `TODO` sem data ou responsável
- Débito técnico intencional deve ser documentado em `tasks/decisions.md`

### Impacto Mínimo

- Mudanças devem tocar apenas o necessário
- Evitar introduzir bugs colaterais
- Preferir mudanças incrementais e reversíveis
- Feature flags para mudanças de alto risco

### Padrões Arquiteturais Preferidos

- Composição > Herança
- Protocol/Interface > Classe concreta
- Injeção de dependência > instanciação direta
- Evento/Callback > polling ativo
- Repositório > acesso direto ao banco de dados
- Configuração externalizada > hardcode

### Comunicação com o Usuário

- Resumir mudanças em alto nível antes de mostrar código
- Destacar trade-offs quando houver mais de uma abordagem válida
- Sinalizar riscos e side effects explicitamente
- Perguntas de clarificação: no máximo 2 por vez, objetivas

### Checklist Universal Pré-Entrega

```
[ ] Testes passando (unitários + integração relevante)
[ ] Lint sem erros (Ruff/mypy para Python; build limpa para C#)
[ ] Sem regressões no comportamento existente
[ ] Documentação atualizada (docstrings, comentários, README se aplicável)
[ ] tasks/lessons.md atualizado se houve correção durante a tarefa
[ ] Um engenheiro sênior aprovaria isso?
```