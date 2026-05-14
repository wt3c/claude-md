---
name: opentelemetry-instrumentation
description: >
  Instrumentar aplicações Python/Django com OpenTelemetry para observabilidade
  via Dynatrace. Usar quando adicionar tracing, métricas ou logs estruturados.
---

# OpenTelemetry + Dynatrace Instrumentation

## Quando aplicar

Esta skill deve ser usada quando:
- Adicionar observabilidade a aplicação Django/Flask/FastAPI
- Instrumentar jobs PySpark ou pipelines de dados
- Debugar problemas de latência ou performance
- Configurar tracing distribuído entre microserviços
- Enviar métricas customizadas para Dynatrace

## Setup Inicial (Django)

### 1. Instalação

```bash
uv pip install \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-instrumentation-django \
  opentelemetry-instrumentation-requests \
  opentelemetry-instrumentation-psycopg2 \
  opentelemetry-exporter-otlp
```

### 2. Configuração Django

```python
# settings.py
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

# Configurar resource (metadados do serviço)
resource = Resource(attributes={
    SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "my-django-app"),
    SERVICE_VERSION: os.getenv("APP_VERSION", "1.0.0"),
    "deployment.environment": os.getenv("ENVIRONMENT", "development"),
})

# Configurar TracerProvider
trace.set_tracer_provider(TracerProvider(resource=resource))

# Configurar exporter para Dynatrace (via OTLP)
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    headers={
        "Authorization": f"Api-Token {os.getenv('DYNATRACE_API_TOKEN')}"
    } if os.getenv('DYNATRACE_API_TOKEN') else {}
)

# Adicionar processor (batch para performance)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# Auto-instrumentar Django
DjangoInstrumentor().instrument()

# Auto-instrumentar requests (chamadas HTTP externas)
RequestsInstrumentor().instrument()

# Auto-instrumentar PostgreSQL
Psycopg2Instrumentor().instrument()
```

### 3. Variáveis de Ambiente

```bash
# .env
OTEL_SERVICE_NAME=my-django-app
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-dynatrace-env.live.dynatrace.com:443
DYNATRACE_API_TOKEN=dt0c01.xxxxxxxxxxxxxxxxxxxx
ENVIRONMENT=production
APP_VERSION=1.2.3
```

## Tracing Manual (Spans Customizados)

### Básico

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id: int):
    """Processa um pedido."""
    with tracer.start_as_current_span("process_order") as span:
        # Adicionar atributos (contexto)
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.priority", "high")
        
        # Lógica de negócio
        order = fetch_order(order_id)
        validate_order(order)
        charge_payment(order)
        ship_order(order)
        
        # Adicionar evento
        span.add_event("order_processed", {
            "order.total": order.total,
            "order.items_count": len(order.items)
        })
```

### Com Exception Handling

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def risky_operation(user_id: int):
    with tracer.start_as_current_span("risky_operation") as span:
        span.set_attribute("user.id", user_id)
        
        try:
            # operação que pode falhar
            result = external_api_call(user_id)
            span.set_status(Status(StatusCode.OK))
            return result
            
        except ExternalAPIError as e:
            # Registrar erro no span
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
```

### Nested Spans (Operações Hierárquicas)

```python
def checkout(cart_id: int):
    with tracer.start_as_current_span("checkout") as parent_span:
        parent_span.set_attribute("cart.id", cart_id)
        
        # Nested span 1
        with tracer.start_as_current_span("validate_cart"):
            validate_cart(cart_id)
        
        # Nested span 2
        with tracer.start_as_current_span("calculate_total") as calc_span:
            total = calculate_total(cart_id)
            calc_span.set_attribute("cart.total", total)
        
        # Nested span 3
        with tracer.start_as_current_span("process_payment"):
            process_payment(cart_id, total)
```

## Atributos Semânticos (Semantic Conventions)

Use atributos padronizados quando possível:

```python
from opentelemetry.semconv.trace import SpanAttributes

with tracer.start_as_current_span("database_query") as span:
    span.set_attribute(SpanAttributes.DB_SYSTEM, "postgresql")
    span.set_attribute(SpanAttributes.DB_NAME, "production")
    span.set_attribute(SpanAttributes.DB_STATEMENT, "SELECT * FROM users WHERE id = ?")
    span.set_attribute(SpanAttributes.DB_USER, "app_user")

with tracer.start_as_current_span("http_request") as span:
    span.set_attribute(SpanAttributes.HTTP_METHOD, "POST")
    span.set_attribute(SpanAttributes.HTTP_URL, "https://api.example.com/users")
    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, 201)
```

## Métricas Customizadas

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Configurar MeterProvider
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    )
)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))

# Criar meter
meter = metrics.get_meter(__name__)

# Counter (incrementa monotonicamente)
order_counter = meter.create_counter(
    name="orders.processed",
    description="Total de pedidos processados",
    unit="1"
)

def process_order(order_id):
    # ... lógica ...
    order_counter.add(1, {"order.type": "online", "order.priority": "high"})

# Histogram (distribuição de valores)
request_duration = meter.create_histogram(
    name="http.request.duration",
    description="Duração de requests HTTP",
    unit="ms"
)

def handle_request(request):
    start = time.time()
    try:
        response = process(request)
        return response
    finally:
        duration = (time.time() - start) * 1000
        request_duration.record(duration, {
            "http.method": request.method,
            "http.route": request.path
        })

# Gauge (valor atual)
active_users = meter.create_up_down_counter(
    name="users.active",
    description="Usuários ativos no momento",
    unit="1"
)

def user_login(user_id):
    active_users.add(1)

def user_logout(user_id):
    active_users.add(-1)
```

## PySpark Instrumentation

```python
from pyspark.sql import SparkSession
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def etl_pipeline(input_path: str, output_path: str):
    """Pipeline ETL com tracing."""
    with tracer.start_as_current_span("etl_pipeline") as span:
        span.set_attribute("input.path", input_path)
        span.set_attribute("output.path", output_path)
        
        spark = SparkSession.builder.appName("etl").getOrCreate()
        
        # Extract
        with tracer.start_as_current_span("extract") as extract_span:
            df = spark.read.parquet(input_path)
            count_input = df.count()
            extract_span.set_attribute("rows.input", count_input)
        
        # Transform
        with tracer.start_as_current_span("transform"):
            df = df.filter(df.value > 0)
            df = df.withColumn("processed_at", F.current_timestamp())
        
        # Load
        with tracer.start_as_current_span("load") as load_span:
            df.write.mode("overwrite").parquet(output_path)
            count_output = df.count()
            load_span.set_attribute("rows.output", count_output)
            load_span.set_attribute("rows.dropped", count_input - count_output)
```

## Logs Estruturados (Correlacionados com Traces)

```python
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Auto-instrumentar logging (adiciona trace_id e span_id aos logs)
LoggingInstrumentor().instrument()

# Configurar logger
logger = logging.getLogger(__name__)

def process_user(user_id: int):
    with tracer.start_as_current_span("process_user") as span:
        span.set_attribute("user.id", user_id)
        
        logger.info(f"Processing user {user_id}")  # log correlacionado com trace
        
        try:
            result = do_something(user_id)
            logger.info(f"User {user_id} processed successfully")
            return result
        except Exception as e:
            logger.error(f"Error processing user {user_id}: {e}", exc_info=True)
            raise
```

## Dynatrace: Visualização e Queries

### DQL (Dynatrace Query Language)

```dql
// Buscar traces lentos
fetch spans
| filter service.name == "my-django-app"
| filter duration > 1000ms
| sort duration desc
| limit 100

// Contar requisições por endpoint
fetch spans
| filter service.name == "my-django-app"
| filter span.kind == "server"
| summarize count = count(), by: {http.route}
| sort count desc

// Calcular P95 de latência
fetch spans
| filter service.name == "my-django-app"
| summarize p95 = percentile(duration, 95), by: {http.route}
```

## Checklist de Instrumentação

```
[ ] Auto-instrumentação configurada (Django, requests, PostgreSQL)
[ ] TracerProvider com resource (service.name, service.version, environment)
[ ] OTLP exporter apontando para Dynatrace
[ ] Variáveis de ambiente configuradas (OTEL_SERVICE_NAME, etc.)
[ ] Spans customizados em operações críticas
[ ] Atributos semânticos usados quando aplicável
[ ] Exception handling com span.record_exception()
[ ] Métricas customizadas (counters, histograms) se necessário
[ ] Logs estruturados correlacionados com traces
[ ] Testes: traces aparecem no Dynatrace
[ ] Dashboards criados para métricas chave (latência, erros, throughput)
```

## Performance Tips

```python
# ❌ ERRADO — criar span para cada item (overhead alto)
for item in items:
    with tracer.start_as_current_span(f"process_{item.id}"):
        process(item)

# ✅ CORRETO — um span para o batch, eventos para itens individuais
with tracer.start_as_current_span("process_batch") as span:
    span.set_attribute("batch.size", len(items))
    for item in items:
        process(item)
        span.add_event("item_processed", {"item.id": item.id})

# ❌ ERRADO — atributos com alta cardinalidade
span.set_attribute("user.email", user.email)  # muitos valores únicos

# ✅ CORRETO — atributos com baixa cardinalidade
span.set_attribute("user.country", user.country)  # poucos valores

# ✅ Usar sampling para ambientes de alto tráfego
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% dos traces
tracer_provider = TracerProvider(
    sampler=TraceIdRatioBased(0.1)
)
```

## Referências

- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/)
- [Dynatrace OpenTelemetry](https://www.dynatrace.com/support/help/extend-dynatrace/opentelemetry)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
