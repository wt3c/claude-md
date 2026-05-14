# Lições Aprendidas

## Python / Django

- [PADRÃO] Usar SQLAlchemy engine para Pandas ↔ banco (evita UserWarning DBAPI2)
- [PADRÃO] UV para todos os projetos Python — nunca pip direto
- [PADRÃO] `infisical run --env=dev --` como prefixo para qualquer comando local com secrets
- [ANTIPADRÃO] `Model.objects.all()` sem select_related quando há FKs acessadas — causa N+1
- [ANTIPADRÃO] Lógica de negócio em views — mover para services

## PySpark / Dados

- [ANTIPADRÃO] `.collect()` sem amostragem prévia → estoura memória do driver
- [ANTIPADRÃO] `.count()` repetido sem `.cache()` → recalcula toda a chain
- [PADRÃO] Validar schema explicitamente antes de qualquer transformação

## GitLab CI/CD

- [PADRÃO] Cache de UV em `.uv-cache/` com key baseada em `uv.lock` reduz tempo de pipeline em ~60%
- [PADRÃO] PostgreSQL como service no CI — usar `POSTGRES_*` variables padrão

## C# / Unity

- [PADRÃO] Evitar singletons estáticos → preferir referências diretas ou UnityEvents
- [ANTIPADRÃO] `FindObjectOfType` em runtime → substituir por injeção via Inspector
- [PADRÃO] ScriptableObjects para todas as configurações tunable

## Observabilidade

- [PADRÃO] Chamar `configure_telemetry()` no `AppConfig.ready()` — garante instrumentação antes das requisições
- [ANTIPADRÃO] Colocar PII em atributos de span — viola LGPD e políticas Dynatrace
