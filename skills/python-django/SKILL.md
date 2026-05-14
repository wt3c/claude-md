---
name: python-django
description: >
  Aplicar padrões de arquitetura Django com Python 3.12, UV, TDD, Ruff, mypy,
  Infisical e observabilidade. Usar quando criar ou refatorar qualquer código
  Python/Django, incluindo models, views, services, tasks Celery, serializers DRF.
---

# Skill: Python / Django — Arquitetura e Qualidade

## Stack obrigatória

- Python 3.12.10 | Django 6.x | PostgreSQL
- Gerenciador: **UV** (nunca pip direto)
- Qualidade: Ruff + mypy | Testes: Pytest com `-n auto` SEMPRE
- Secrets: Infisical (nunca hardcode)

## Comandos essenciais

```bash
uv add <pacote>                             # adicionar dependência
uv run python manage.py migrate            # migrations
uv run python manage.py makemigrations     # gerar migration
uv run pytest -n auto --cov               # testes com cobertura
uv run ruff check . --fix && uv run ruff format .
uv run mypy .
infisical run -- uv run python manage.py runserver
```

## TDD — Ciclo obrigatório

```
RED   → Escrever teste que falha
GREEN → Código mínimo para passar
REFACTOR → Melhorar sem quebrar testes
```

Nunca escrever código de produção sem teste correspondente.

## Estrutura de Projeto (padrão)

```
apps/
  nome_do_app/
    models.py         # dados e validação simples (sem lógica de negócio)
    services.py       # lógica de negócio (sem import de request)
    repositories.py   # acesso a dados — sempre via Protocol
    views.py          # orquestração HTTP (sem lógica de negócio)
    serializers.py    # validação input/output DRF
    tasks.py          # Celery tasks (idempotentes)
    admin.py
    apps.py
    urls.py
    tests/
      __init__.py
      test_models.py
      test_services.py
      test_views.py
      test_repositories.py
      conftest.py
```

## Protocol-based DI (padrão obrigatório)

```python
from typing import Protocol
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User: ...

    def save(self, user: User) -> User: ...

    def find_by_email(self, email: str) -> User | None: ...


class DjangoUserRepository:
    def get_by_id(self, user_id: int) -> User:
        return User.objects.get(pk=user_id)

    def save(self, user: User) -> User:
        user.full_clean()
        user.save()
        return user

    def find_by_email(self, email: str) -> User | None:
        return User.objects.filter(email=email).first()


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def activate_user(self, user_id: int) -> User:
        user = self._repo.get_by_id(user_id)
        user.is_active = True
        return self._repo.save(user)
```

## Regras fundamentais

- Services nunca importam `request`, `HttpRequest` ou similares
- Services recebem dados puros (int, str, dataclass) — não objetos HTTP
- Views nunca contêm lógica de negócio
- Models apenas dados, validação `clean()` e `__str__`
- `select_related` / `prefetch_related` obrigatório em queries com relacionamentos
- Nunca `Model.objects.all()` em views — sempre filtrar ou paginar
- Migrations: nunca modificar migration já aplicada em produção

## Legado

- Escrever testes de caracterização **antes** de refatorar
- Padrões incrementais: Chain of Responsibility, Repository, Strategy
- Nunca quebrar API pública sem aprovação explícita
- Commits atômicos e rastreáveis

## Ciclo de Qualidade

```bash
uv run ruff check . --fix && uv run ruff format .
uv run mypy .
uv run pytest --cov --cov-report=term-missing -n auto
```

## Infisical — Uso correto

```python
# settings/base.py — sempre no topo, antes de qualquer os.environ[]
from secretsloader import load_secrets

load_secrets()
```

O `load_secrets()` lê as variáveis de conexão do `.env` e injeta todos os secrets  
do projeto Infisical no `os.environ`. Após a chamada, acessar normalmente:

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
    }
}
```

`.env` contém apenas as credenciais de acesso ao Infisical (nunca commitar):

```dotenv
INFISICAL_PROJECT_ID=
INFISICAL_TOKEN=
INFISICAL_SITE_URL=https://ncd-infisical.mprj.mp.br/
INFISICAL_PORT=80
INFISICAL_ENVIRONMENT_SLUG=prod
```

## Checklist pré-entrega Python/Django

```
[ ] TDD respeitado: todo código novo tem teste correspondente
[ ] uv run ruff check . --fix   → sem erros
[ ] uv run ruff format .        → formatação aplicada
[ ] uv run mypy .               → sem erros de tipo
[ ] uv run pytest -n auto --cov → ≥ 80% cobertura em código novo
[ ] Nenhum secret hardcoded (grep -r "password\|token\|secret" --include="*.py")
[ ] select_related/prefetch_related em todas as queries com FK
[ ] Migrations geradas e sem conflito
[ ] Admin registrado para modelos novos
```
