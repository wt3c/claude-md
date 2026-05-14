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
uv add secretsloader
```

## Uso — carregamento de secrets

```python
from secretsloader import load_secrets

load_secrets()
```

Chamar no início da aplicação (antes de qualquer acesso a variáveis de ambiente).  
Em Django: chamar em `AppConfig.ready()` ou no topo de `settings/base.py`.

## .env — Variáveis de conexão com o Infisical

O `.env` contém **apenas** as credenciais de acesso ao Infisical, não os secrets da aplicação.  
O `load_secrets()` usa essas variáveis para buscar e injetar todos os secrets do projeto no ambiente.

```dotenv
# Infisical
INFISICAL_PROJECT_ID=
INFISICAL_TOKEN=
INFISICAL_SITE_URL=https://ncd-infisical.mprj.mp.br/
INFISICAL_PORT=80

# dev | staging | prod
INFISICAL_ENVIRONMENT_SLUG=prod
```

## Integração com Django

```python
# settings/base.py
from secretsloader import load_secrets

load_secrets()  # injeta os secrets do Infisical no os.environ

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

## CI/CD — GitLab

O `load_secrets()` é chamado automaticamente no startup da aplicação (settings).  
No CI, basta definir as variáveis de conexão como **GitLab CI Variables masked** —  
não é necessário nenhum passo adicional no `before_script`.

```
# GitLab CI Variables (masked — não são secrets da aplicação):
INFISICAL_PROJECT_ID       → ID do projeto no Infisical
INFISICAL_TOKEN            → Token de acesso (Machine Identity)
INFISICAL_SITE_URL         → https://ncd-infisical.mprj.mp.br/
INFISICAL_PORT             → 80
INFISICAL_ENVIRONMENT_SLUG → dev | staging | prod
```

```yaml
# .gitlab-ci.yml — nenhum passo extra necessário
before_script:
  - uv sync

test:
  script:
    - uv run pytest -n auto --cov  # load_secrets() é chamado pelo settings.py
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
