# Architecture Decision Records (ADRs)

> Este arquivo registra decisões arquiteturais importantes do projeto.  
> Use o template abaixo para cada nova decisão.

---

## ADR-001: Adoção do UV como gerenciador de pacotes Python

**Status:** Aceito  
**Data:** 2026-05-14  
**Decisor(es):** Time de Desenvolvimento

### Contexto

O projeto usa Python 3.12+ e precisa de gerenciamento de dependências rápido, reproduzível e compatível com CI/CD. Atualmente as opções principais são:

- **pip:** lento, não reproduzível por padrão
- **poetry:** melhor que pip, mas ainda lento em grandes projetos
- **uv:** novo gerenciador ultrarrápido (escrito em Rust), compatível com pip

### Decisão

Adotar **UV** como gerenciador de pacotes padrão para todos os projetos Python.

### Alternativas Consideradas

1. **pip + requirements.txt** — rejeitada porque:
   - Lento (10-50x mais lento que uv)
   - Não reproduzível sem lockfile
   - Resolução de dependências fraca

2. **poetry** — rejeitada porque:
   - Ainda significativamente mais lento que uv
   - Overhead desnecessário para projetos simples
   - Incompatibilidades ocasionais com packages específicos

3. **uv** — **ACEITA** porque:
   - 10-100x mais rápido que pip
   - Compatível com requirements.txt e pyproject.toml
   - Reproduzível por padrão
   - Zero configuração adicional

### Consequências

**Positivas:**
- Instalação de dependências 10-100x mais rápida localmente e em CI/CD
- Builds reproduzíveis sem configuração extra
- Sintaxe familiar (compatível com pip)
- Redução de tempo de pipeline GitLab CI

**Negativas:**
- Ferramenta relativamente nova (menos madura que poetry/pip)
- Time precisa aprender novo comando (mitigado por compatibilidade com pip)
- Possíveis bugs/edge cases não descobertos ainda

**Neutras:**
- Comandos muito similares ao pip (`uv pip install` vs `pip install`)
- Arquivos de configuração permanecem os mesmos (requirements.txt, pyproject.toml)

### Notas de Implementação

```bash
# Instalação global (uma vez)
pip install uv

# Uso no projeto
uv venv                              # criar venv
uv pip install -r requirements.txt   # instalar deps
uv pip compile pyproject.toml -o requirements.txt  # gerar lockfile
uv run pytest                        # rodar comando no venv

# GitLab CI
before_script:
  - pip install uv
  - uv pip install -r requirements.txt
```

**Referências:**
- [UV Docs](https://github.com/astral-sh/uv)
- [UV vs pip benchmark](https://github.com/astral-sh/uv#benchmarks)

---

## ADR-002: Service Layer Pattern para Django

**Status:** Aceito  
**Data:** 2026-05-14  
**Decisor(es):** Time de Desenvolvimento

### Contexto

O projeto Django tem lógica de negócio espalhada entre Views, Models e Serializers, dificultando:
- Testes unitários (dependem de request/response HTTP)
- Reutilização de lógica (duplicação entre views e tasks)
- Separação de responsabilidades

### Decisão

Adotar **Service Layer Pattern** com Protocol-based Dependency Injection para centralizar lógica de negócio.

### Alternativas Consideradas

1. **Fat Models** (lógica nos Models) — rejeitada porque:
   - Mistura persistência com lógica de negócio (SRP violation)
   - Dificulta testes (precisa de banco)
   - Models ficam gigantes e difíceis de manter

2. **Lógica nas Views** — rejeitada porque:
   - Testes dependem de HTTP mocking
   - Impossível reutilizar entre views, tasks, scripts
   - Views gigantes e difíceis de ler

3. **Service Layer + Repository** — **ACEITA** porque:
   - Lógica de negócio testável sem HTTP ou banco
   - Reutilizável em views, tasks, scripts, CLI
   - Separação clara de responsabilidades (SRP + DIP)

### Consequências

**Positivas:**
- Lógica de negócio 100% testável sem mocks complexos
- Reutilização entre views, tasks Celery, scripts
- Código mais limpo e fácil de manter
- Facilita onboarding de novos devs

**Negativas:**
- Mais arquivos/estrutura (services.py, repositories.py)
- Curva de aprendizado inicial para o time
- Boilerplate adicional (Protocols, DI manual)

**Neutras:**
- Views ficam menores (apenas orquestração HTTP)
- Models ficam menores (apenas dados + validação simples)

### Notas de Implementação

```python
# apps/users/repositories.py
from typing import Protocol
from .models import User

class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User: ...
    def save(self, user: User) -> User: ...

class DjangoUserRepository:
    def get_by_id(self, user_id: int) -> User:
        return User.objects.get(id=user_id)
    
    def save(self, user: User) -> User:
        user.save()
        return user

# apps/users/services.py
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def activate_user(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        user.is_active = True
        return self.repository.save(user)

# apps/users/views.py (DRF)
class UserActivateView(APIView):
    def post(self, request, user_id):
        service = UserService(DjangoUserRepository())
        user = service.activate_user(user_id)
        return Response(UserSerializer(user).data)
```

**Referências:**
- [Django Service Layer Pattern](https://www.dabapps.com/insights/django-models-and-encapsulation/)
- [Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)

---

## Template para Novas Decisões

```markdown
## ADR-XXX: [Título da decisão]

**Status:** Proposto | Aceito | Implementado | Depreciado  
**Data:** YYYY-MM-DD  
**Decisor(es):** [nomes]

### Contexto

[Descrever o problema ou necessidade que motivou a decisão]

### Decisão

[Qual foi a decisão tomada]

### Alternativas Consideradas

1. **Alternativa A:** [descrição] — rejeitada porque [motivo]
2. **Alternativa B:** [descrição] — rejeitada porque [motivo]
3. **Alternativa C:** [descrição] — **ACEITA** porque [motivo]

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

[Detalhes técnicos, código exemplo, links, referências]
```
