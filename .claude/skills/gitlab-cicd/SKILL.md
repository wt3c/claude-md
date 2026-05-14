---
name: gitlab-cicd
description: >
  Configurar pipelines GitLab CI/CD otimizados para Python/Django,
  PySpark, Unity, com cache, paralelismo e deploy automático.
---

# GitLab CI/CD Pattern

## Quando aplicar

Esta skill deve ser usada quando:
- Criar novo pipeline GitLab CI/CD
- Otimizar pipeline existente (velocidade, cache)
- Configurar deploy automático (staging, production)
- Integrar testes, lint, security scans
- Configurar GitLab on-premise (MPRJ ou similar)

## Estrutura Básica: Python/Django

```yaml
# .gitlab-ci.yml
image: python:3.12

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  UV_CACHE_DIR: "$CI_PROJECT_DIR/.cache/uv"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/pip
    - .cache/uv
    - .venv/

stages:
  - test
  - build
  - deploy

before_script:
  - pip install uv
  - uv venv
  - source .venv/bin/activate
  - uv pip install -r requirements.txt

# ========== STAGE: TEST ==========

lint:
  stage: test
  script:
    - ruff check .
    - ruff format --check .
  only:
    - merge_requests
    - main

type-check:
  stage: test
  script:
    - mypy .
  allow_failure: true  # warnings não bloqueiam pipeline
  only:
    - merge_requests
    - main

unit-tests:
  stage: test
  script:
    - pytest -n auto --cov --cov-report=term --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  only:
    - merge_requests
    - main

security-scan:
  stage: test
  script:
    - pip install bandit safety
    - bandit -r apps/ -f json -o bandit-report.json || true
    - safety check --json > safety-report.json || true
  artifacts:
    reports:
      sast: bandit-report.json
    paths:
      - safety-report.json
  only:
    - main

# ========== STAGE: BUILD ==========

build-docker:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main

# ========== STAGE: DEPLOY ==========

deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_STAGING
    - kubectl set image deployment/my-app my-app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n staging
    - kubectl rollout status deployment/my-app -n staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

deploy-production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_PRODUCTION
    - kubectl set image deployment/my-app my-app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n production
    - kubectl rollout status deployment/my-app -n production
  environment:
    name: production
    url: https://example.com
  when: manual  # deploy manual para produção
  only:
    - main
```

## Otimizações de Performance

### 1. Cache de Dependências

```yaml
# Cache global (compartilhado entre jobs)
cache:
  key: ${CI_COMMIT_REF_SLUG}  # cache por branch
  paths:
    - .cache/pip
    - .cache/uv
    - .venv/
    - node_modules/  # se tiver frontend

# Cache por job (se necessário cache específico)
unit-tests:
  cache:
    key: test-${CI_COMMIT_REF_SLUG}
    paths:
      - .venv/
      - .pytest_cache/
```

### 2. Paralelismo

```yaml
# Testes em paralelo (matriz de Python versions)
test:python-matrix:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.10", "3.11", "3.12"]
  image: python:${PYTHON_VERSION}
  script:
    - pytest -n auto

# Jobs paralelos (diferentes tarefas)
test:
  stage: test
  parallel:
    - lint
    - type-check
    - unit-tests
    - integration-tests
```

### 3. Artifacts Seletivos

```yaml
unit-tests:
  artifacts:
    when: always  # upload mesmo se job falhar
    expire_in: 1 week
    paths:
      - coverage.xml
      - htmlcov/
    reports:
      junit: test-reports/*.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### 4. Rules (em vez de only/except)

```yaml
# Mais flexível que only/except
unit-tests:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG'

# Evitar duplicação de pipelines
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS'
      when: never
    - if: '$CI_COMMIT_BRANCH'
```

## GitLab on-premise (MPRJ)

```yaml
# Configuração para GitLab on-premise
variables:
  GITLAB_API_URL: "https://gitlab-dti.mprj.mp.br/api/v4"
  CI_REGISTRY: "gitlab-dti.mprj.mp.br:5050"

# Usar runners específicos
unit-tests:
  tags:
    - mprj-runner  # runner configurado no GitLab MPRJ
    - docker
```

## PySpark Pipeline

```yaml
# .gitlab-ci.yml para jobs PySpark
spark-etl:
  stage: deploy
  image: bitnami/spark:3.4
  script:
    - spark-submit \
        --master yarn \
        --deploy-mode cluster \
        --conf spark.executor.memory=4g \
        --conf spark.executor.cores=2 \
        --conf spark.dynamicAllocation.enabled=true \
        jobs/etl_vendas.py \
        --input hdfs://vendas_raw/$CI_COMMIT_SHA \
        --output hdfs://vendas_processadas/$CI_COMMIT_SHA
  only:
    - schedules  # rodar via schedule (cron)
```

## Unity Build (Android)

```yaml
# .gitlab-ci.yml para Unity
unity-build-android:
  stage: build
  image: unityci/editor:ubuntu-2022.3.10f1-android-1
  before_script:
    - chmod +x ./ci/activate_unity_license.sh
    - ./ci/activate_unity_license.sh
  script:
    - /opt/unity/Editor/Unity \
        -quit -batchmode -nographics \
        -projectPath . \
        -buildTarget Android \
        -executeMethod BuildScript.BuildAndroid \
        -logFile /dev/stdout
  artifacts:
    paths:
      - Builds/*.apk
      - Builds/*.aab
    expire_in: 1 week
  only:
    - tags

# BuildScript.cs (Unity)
public static class BuildScript
{
    public static void BuildAndroid()
    {
        BuildPlayerOptions options = new BuildPlayerOptions();
        options.scenes = EditorBuildSettings.scenes.Select(s => s.path).ToArray();
        options.locationPathName = "Builds/game.apk";
        options.target = BuildTarget.Android;
        options.options = BuildOptions.None;
        
        BuildPipeline.BuildPlayer(options);
    }
}
```

## Secrets Management

```yaml
# Usar GitLab CI/CD Variables (Settings → CI/CD → Variables)

# Protected: apenas branches protegidas (main, tags)
# Masked: valor nunca aparece nos logs

deploy-production:
  script:
    - echo "Deploying with API_KEY=$API_KEY"  # masked, não aparece nos logs
  environment:
    name: production
```

## Scheduled Pipelines

```yaml
# Pipeline agendado (Settings → CI/CD → Schedules)
# Criar schedule: daily-etl @ 0 2 * * * (2h da manhã)

etl-daily:
  stage: deploy
  script:
    - python jobs/etl_vendas.py --date $(date +%Y-%m-%d)
  only:
    - schedules
  variables:
    SCHEDULE_NAME: "daily-etl"
```

## Merge Request Pipelines

```yaml
# Rodar testes apenas em MRs
mr-tests:
  stage: test
  script:
    - pytest -n auto
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# Comentar cobertura no MR
coverage-comment:
  stage: test
  needs: [unit-tests]
  script:
    - |
      COVERAGE=$(grep -oP 'TOTAL.*\K\d+' coverage.txt)
      curl -X POST \
        -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID/notes" \
        -d "body=Coverage: ${COVERAGE}%"
  only:
    - merge_requests
```

## Deploy Review Apps

```yaml
# Ambiente temporário para cada MR
review:
  stage: deploy
  script:
    - helm upgrade --install \
        --set image.tag=$CI_COMMIT_SHA \
        --namespace review-$CI_MERGE_REQUEST_IID \
        my-app ./helm/chart
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    url: https://review-$CI_MERGE_REQUEST_IID.example.com
    on_stop: stop-review
    auto_stop_in: 1 week
  only:
    - merge_requests

stop-review:
  stage: deploy
  script:
    - helm uninstall my-app --namespace review-$CI_MERGE_REQUEST_IID
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    action: stop
  when: manual
  only:
    - merge_requests
```

## Checklist de Pipeline

```
[ ] Stages bem definidos (test, build, deploy)
[ ] Cache de dependências configurado
[ ] Testes rodando em paralelo (pytest -n auto)
[ ] Lint e type-check como jobs separados
[ ] Security scan (bandit, safety)
[ ] Coverage report integrado
[ ] Artifacts com expire_in configurado
[ ] Secrets via GitLab CI/CD Variables (masked)
[ ] Deploy staging automático
[ ] Deploy production manual
[ ] Tags específicos para runners
[ ] Otimizações de performance aplicadas
```

## Referências

- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)
- [GitLab CI/CD YAML Reference](https://docs.gitlab.com/ee/ci/yaml/)
- [GitLab Runner](https://docs.gitlab.com/runner/)
