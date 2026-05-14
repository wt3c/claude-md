---
name: opentelemetry
description: >
  Instrumentar aplicações Python/Django com OpenTelemetry e exportar traces/métricas
  para Dynatrace. Usar quando adicionar observabilidade, rastreamento distribuído,
  métricas customizadas ou configurar exporters OTLP.
---

# Skill: OpenTelemetry + Dynatrace

## Stack

- opentelemetry-sdk | opentelemetry-instrumentation-django
- opentelemetry-exporter-otlp | Dynatrace (OTLP ingest)

## Instalação (UV)

```bash
uv add opentelemetry-sdk \
       opentelemetry-api \
       opentelemetry-instrumentation-django \
       opentelemetry-instrumentation-psycopg2 \
       opentelemetry-instrumentation-celery \
       opentelemetry-exporter-otlp-proto-grpc
```

## Configuração — Django

```python
# config/telemetry.py
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor


def configure_telemetry(service_name: str) -> None:
    """Inicializar telemetria — chamar em AppConfig.ready() ou wsgi.py."""
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    dt_token = os.environ.get("DT_API_TOKEN")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Api-Token {dt_token}"

    # Traces
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Métricas
    metric_exporter = OTLPMetricExporter(endpoint=endpoint, headers=headers)
    meter_provider = MeterProvider(
        metric_readers=[PeriodicExportingMetricReader(metric_exporter)]
    )
    metrics.set_meter_provider(meter_provider)

    # Auto-instrumentação
    DjangoInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    CeleryInstrumentor().instrument()
```

```python
# apps.py (de qualquer app Django)
from django.apps import AppConfig


class MinhaAppConfig(AppConfig):
    name = "apps.minha_app"

    def ready(self) -> None:
        from config.telemetry import configure_telemetry
        configure_telemetry(service_name="minha-app")
```

## Spans Manuais em Services

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class UserService:
    def activate_user(self, user_id: int) -> User:
        with tracer.start_as_current_span("user.activate") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("service.name", "user-service")
            try:
                user = self._repo.get_by_id(user_id)
                user.is_active = True
                result = self._repo.save(user)
                span.set_attribute("user.email", result.email)
                return result
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR, str(exc))
                raise
```

## Métricas Customizadas

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

# Contador
request_counter = meter.create_counter(
    name="app.requests.total",
    description="Total de requisições processadas",
    unit="1",
)

# Histograma para latência
request_duration = meter.create_histogram(
    name="app.request.duration",
    description="Duração das requisições em milissegundos",
    unit="ms",
)

# Uso em código
request_counter.add(1, {"endpoint": "/api/users", "method": "GET"})
```

## Variáveis de Ambiente (via Infisical)

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://xxxxx.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.xxxxxxxxxxxxxxxxxxxx
OTEL_SERVICE_NAME=minha-app-prod
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=prod,service.version=1.2.3
```

## Dynatrace — Configuração OTLP Ingest

```
1. Dynatrace → Settings → OpenTelemetry → Ingest endpoint
2. Copiar endpoint OTLP gRPC
3. Criar API Token com permissões: openTelemetryTrace.ingest, metrics.ingest
4. Guardar no Infisical (nunca no código)
```

## Checklist de Observabilidade

```
[ ] configure_telemetry() chamado no startup da aplicação
[ ] Endpoints críticos com spans manuais e atributos relevantes
[ ] Exceções registradas com span.record_exception()
[ ] Variáveis OTEL_* no Infisical (não hardcoded)
[ ] Dashboard básico criado no Dynatrace para o serviço
[ ] Alertas configurados para erros críticos no Dynatrace
[ ] Nenhum dado pessoal (PII) em atributos de span
```
