---
name: gitlab-ci
description: >
  Criar e depurar pipelines GitLab CI/CD para o GitLab on-premise do MPRJ.
  Usar quando criar ou modificar .gitlab-ci.yml, configurar runners, variáveis,
  environments ou qualquer integração com gitlab-dti.mprj.mp.br.
---

# Skill: GitLab CI/CD — MPRJ On-Premise

## Instância

- **URL:** `https://gitlab-dti.mprj.mp.br/`
- **Auth:** Personal Access Token ou Project Access Token
- **Runners:** Shared runners do MPRJ ou runners específicos do projeto

## Autenticação GitLab API via MCP

```bash
# Variáveis obrigatórias (nunca commitar)
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_URL="https://gitlab-dti.mprj.mp.br"

# Configurar MCP (escopo local — não commitado)
claude mcp add --scope local gitlab -- npx -y @modelcontextprotocol/server-gitlab \
  --gitlab-url "$GITLAB_URL" \
  --token "$GITLAB_TOKEN"
```

## Template `.gitlab-ci.yml` — Python/Django

```yaml
image: python:3.12-slim

stages:
  - quality
  - test
  - build
  - deploy

variables:
  UV_SYSTEM_PYTHON: "1"
  UV_CACHE_DIR: ".uv-cache"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .uv-cache/
    - .pip-cache/

before_script:
  - pip install uv --quiet
  - uv sync --quiet

# ── Quality ────────────────────────────────────────────────────────────────────
ruff:
  stage: quality
  script:
    - uv run ruff check . --output-format=gitlab
    - uv run ruff format . --check
  artifacts:
    reports:
      codequality: gl-code-quality-report.json

mypy:
  stage: quality
  script:
    - uv run mypy . --junit-xml=mypy-report.xml
  artifacts:
    reports:
      junit: mypy-report.xml

# ── Tests ──────────────────────────────────────────────────────────────────────
pytest:
  stage: test
  services:
    - postgres:15
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    DATABASE_URL: "postgresql://postgres:postgres@postgres:5432/test_db"
  script:
    - uv run pytest -n auto --cov --cov-report=xml --junitxml=junit-report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      junit: junit-report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

# ── Build ──────────────────────────────────────────────────────────────────────
build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  only:
    - main
    - develop

# ── Deploy ─────────────────────────────────────────────────────────────────────
deploy-dev:
  stage: deploy
  environment:
    name: development
    url: https://app-dev.mprj.mp.br
  script:
    - echo "Deploy para desenvolvimento"
  only:
    - develop
  when: on_success
```

## Convenções de Branch MPRJ

```
main         # produção — protegida, apenas MR
develop      # integração — protegida
feature/*    # novas funcionalidades
fix/*        # correções de bug
hotfix/*     # correção urgente em produção
release/*    # preparação de release
```

## Merge Request — Template

```markdown
## O que foi feito
- [ ] Descreva as mudanças

## Como testar
1. Passo 1
2. Passo 2

## Checklist
- [ ] Testes passando no pipeline
- [ ] Cobertura ≥ 80%
- [ ] Sem secrets no código
- [ ] CLAUDE.md local atualizado se necessário

## Issues relacionadas
Closes #
```

## Secrets via Infisical no CI

```yaml
# Não usar GitLab CI variables para secrets — usar Infisical Machine Identity
before_script:
  - |
    export INFISICAL_TOKEN=$(infisical login \
      --method=universal-auth \
      --client-id=$INFISICAL_CLIENT_ID \
      --client-secret=$INFISICAL_CLIENT_SECRET \
      --plain)
  - infisical run -- uv sync
```

## Operações comuns via MCP GitLab

```
"Liste os MRs abertos no projeto X"
"Mostre o status do último pipeline da branch develop"
"Crie um MR de feature/nova-feature para develop"
"Adicione o label 'needs-review' no MR #123"
"Mostre os jobs falhando no pipeline #456"
"Aprove o MR #78 (se tenho permissão)"
```

## Troubleshooting comum

```bash
# Runner sem permissão para registry
# → Checar "Allow access to the GitLab Container Registry" no runner config

# Pipeline não dispara em push
# → Verificar .gitlab-ci.yml: only/except ou rules corretas

# Cache não funciona
# → key: $CI_COMMIT_REF_SLUG  ou  key: files: [uv.lock]

# Teste de DB falha no CI
# → Aguardar serviço: services: [postgres:15], variáveis POSTGRES_*
```
