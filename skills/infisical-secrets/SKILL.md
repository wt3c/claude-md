---
name: infisical-secrets
description: >
  Integrar Infisical para gestão de secrets em projetos Python/Django, CI/CD e
  ambientes locais. Usar quando configurar secrets, variáveis de ambiente ou
  qualquer aspecto de gerenciamento de credenciais.
---

# Skill: Infisical — Gestão de Secrets

## Princípio fundamental

**Nenhum secret** vai para código, `.env` commitado, CLAUDE.md, ou variáveis GitLab CI em texto plano.  
Tudo passa pelo Infisical.

## Instalação (UV)

```bash
uv add infisical-sdk
```

## CLI — Desenvolvimento Local

```bash
# Autenticar (uma vez)
infisical login

# Rodar qualquer comando com secrets injetados
infisical run --env=dev -- python manage.py runserver
infisical run --env=dev -- uv run pytest -n auto
infisical run --env=dev -- uv run python manage.py migrate

# Ver secrets do ambiente
infisical secrets --env=dev
```

## SDK Python — Integração em Django

```python
# config/infisical.py
import os
from functools import lru_cache
from infisical_sdk import InfisicalClient


@lru_cache(maxsize=None)
def get_infisical_client() -> InfisicalClient:
    return InfisicalClient(
        token=os.environ["INFISICAL_TOKEN"],
        site_url=os.environ.get("INFISICAL_URL", "https://app.infisical.com"),
    )


def get_secret(name: str, environment: str | None = None) -> str:
    env = environment or os.environ.get("APP_ENV", "dev")
    client = get_infisical_client()
    return client.secrets.get(secret_name=name, environment=env).secret_value
```

```python
# settings/base.py
from config.infisical import get_secret

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_secret("DB_NAME"),
        "USER": get_secret("DB_USER"),
        "PASSWORD": get_secret("DB_PASSWORD"),
        "HOST": get_secret("DB_HOST"),
        "PORT": get_secret("DB_PORT", environment="shared"),
    }
}
```

## CI/CD — Machine Identity (GitLab)

```yaml
# .gitlab-ci.yml
before_script:
  - pip install infisical --quiet
  - |
    export INFISICAL_TOKEN=$(infisical login \
      --method=universal-auth \
      --client-id=$INFISICAL_CLIENT_ID \
      --client-secret=$INFISICAL_CLIENT_SECRET \
      --plain)
```

```
# GitLab CI Variables (apenas estas — não são secrets reais):
INFISICAL_CLIENT_ID     → ID da Machine Identity do projeto
INFISICAL_CLIENT_SECRET → Secret da Machine Identity (marcar como "Masked")
```

## Estrutura de Ambientes

```
dev        → desenvolvimento local
staging    → homologação (MPRJ staging)
prod       → produção (MPRJ produção)
shared     → secrets compartilhados (ex: endpoints de infra)
```

## Regras de segurança

```
[ ] NUNCA commitar .env com valores reais
[ ] NUNCA colocar token Infisical em código
[ ] NUNCA passar secrets como argumentos de linha de comando (ficam no history)
[ ] NUNCA logar secrets (nem em nível DEBUG)
[ ] Usar Machine Identity para CI/CD (não Personal Token)
[ ] Rotacionar tokens a cada 90 dias
[ ] Separar secrets por ambiente (dev/staging/prod)
```

## .gitignore obrigatório

```gitignore
# Secrets — nunca commitar
.env
.env.*
*.env
infisical.json
.infisical.json
```
