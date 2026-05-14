---
description: Consulta Dynatrace para métricas, traces e logs da aplicação
---

Consulte o Dynatrace para verificar saúde e performance da aplicação:

## 1. Métricas Principais (via DQL)

### Latência (P95)

```dql
fetch spans
| filter service.name == "{{service_name}}"
| filter span.kind == "server"
| summarize p95_latency = percentile(duration, 95), by: {http.route}
| sort p95_latency desc
```

### Taxa de Erros

```dql
fetch spans
| filter service.name == "{{service_name}}"
| summarize 
    total = count(),
    errors = countIf(status == "ERROR"),
    error_rate = errors / total * 100
| fieldsAdd error_rate
```

### Throughput (Requests/min)

```dql
fetch spans
| filter service.name == "{{service_name}}"
| filter span.kind == "server"
| summarize count(), by: {bin(timestamp, 1m)}
```

## 2. Traces Lentos

Identificar requisições acima do threshold:

```dql
fetch spans
| filter service.name == "{{service_name}}"
| filter duration > 1000ms
| sort duration desc
| limit 20
| fieldsKeep timestamp, duration, http.route, trace_id
```

## 3. Erros Recentes

```dql
fetch spans
| filter service.name == "{{service_name}}"
| filter status == "ERROR"
| filter timestamp > now() - 1h
| sort timestamp desc
| limit 50
```

## 4. Database Queries Lentas

```dql
fetch spans
| filter service.name == "{{service_name}}"
| filter db.system == "postgresql"
| filter duration > 500ms
| summarize 
    count = count(),
    avg_duration = avg(duration),
    by: {db.statement}
| sort count desc
```

## 5. Dependency Analysis

Verificar latência de serviços downstream:

```dql
fetch spans
| filter service.name == "{{service_name}}"
| filter span.kind == "client"
| summarize 
    count = count(),
    p95_latency = percentile(duration, 95),
    by: {peer.service}
| sort p95_latency desc
```

## 6. Custom Metrics

Se houver métricas customizadas (OpenTelemetry):

```dql
timeseries avg(orders.processed), by: {order.type}

timeseries percentile(http.request.duration, 95), by: {http.route}
```

## 7. Logs Correlacionados

Para um trace específico:

```dql
fetch logs
| filter trace_id == "{{trace_id}}"
| sort timestamp asc
```

## Formato de Saída

```markdown
# Dynatrace Health Check: {{service_name}}

## Resumo (Última 1h)

- **Throughput:** [req/min]
- **Latência P95:** [ms]
- **Taxa de Erros:** [%]
- **Disponibilidade:** [%]

## 🔴 Alertas Críticos

1. [Alerta 1: descrição, impacto, ação recomendada]
2. [Alerta 2: descrição, impacto, ação recomendada]

## ⚠️ Avisos

1. [Aviso 1: descrição]
2. [Aviso 2: descrição]

## 📊 Métricas Detalhadas

### Top 5 Endpoints Mais Lentos (P95)
1. `POST /api/orders` - 1,234ms
2. `GET /api/products` - 987ms
...

### Top 5 Queries Mais Lentas
1. `SELECT * FROM orders WHERE...` - 543ms (142 execuções)
2. `SELECT * FROM users WHERE...` - 432ms (89 execuções)
...

### Erros Recentes
- `DatabaseError: connection timeout` - 12 ocorrências
- `ValidationError: invalid input` - 8 ocorrências

## 🔗 Links Úteis

- [Dynatrace Dashboard](https://dynatrace-env.live.dynatrace.com/...)
- [Traces Lentos](https://dynatrace-env.live.dynatrace.com/...)
- [Logs de Erro](https://dynatrace-env.live.dynatrace.com/...)

## Recomendações

1. [Ação recomendada 1]
2. [Ação recomendada 2]
```

## Variáveis Necessárias

- `service_name`: Nome do serviço no OpenTelemetry (ex: "my-django-app")
- `dynatrace_env`: URL do ambiente Dynatrace
- `trace_id`: ID de trace específico (opcional, para debug)

## Acesso via API (alternativa)

```python
import requests
import os

DYNATRACE_API_URL = os.getenv("DYNATRACE_API_URL")
DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN")

headers = {
    "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}",
    "Content-Type": "application/json"
}

# Query DQL via API
query = """
fetch spans
| filter service.name == "my-django-app"
| summarize p95 = percentile(duration, 95)
"""

response = requests.post(
    f"{DYNATRACE_API_URL}/platform/storage/query/v1/query:execute",
    headers=headers,
    json={"query": query}
)

print(response.json())
```
