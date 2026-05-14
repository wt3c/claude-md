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

## Infisical — Uso correto

```python
import os
from infisical_sdk import InfisicalClient

# inicialização (uma vez, no settings ou AppConfig.ready())
_client = InfisicalClient(
    token=os.environ["INFISICAL_TOKEN"],
    site_url=os.environ.get("INFISICAL_URL", "https://app.infisical.com"),
)


def get_secret(name: str, environment: str = "dev") -> str:
    return _client.secrets.get(secret_name=name, environment=environment).secret_value
```

```bash
# Desenvolvimento local
infisical run --env=dev -- uv run python manage.py runserver

# CI/CD — Machine Identity
export INFISICAL_TOKEN=$(infisical login --method=universal-auth \
  --client-id=$INFISICAL_CLIENT_ID \
  --client-secret=$INFISICAL_CLIENT_SECRET \
  --plain)
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
