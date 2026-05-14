---
name: pyspark-pipeline
description: >
  Criar pipelines PySpark otimizados e testáveis para ETL/ELT.
  Usar quando processar grandes volumes de dados, criar DAGs Airflow,
  ou otimizar jobs Spark existentes.
---

# PySpark Pipeline Pattern

## Quando aplicar

Esta skill deve ser usada quando:
- Criar novo job PySpark para ETL/ELT
- Otimizar job Spark existente (performance, memória)
- Integrar PySpark com Airflow
- Processar dados no Hadoop HDFS
- Escrever testes para lógica de transformação Spark

## Estrutura de Pipeline

```python
# jobs/etl_vendas.py
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from typing import Protocol

class DataSource(Protocol):
    """Interface para fontes de dados."""
    def read(self, spark: SparkSession) -> DataFrame: ...

class DataSink(Protocol):
    """Interface para destinos de dados."""
    def write(self, df: DataFrame) -> None: ...

class VendasPipeline:
    """Pipeline de ETL de vendas."""
    
    def __init__(self, source: DataSource, sink: DataSink):
        self.source = source
        self.sink = sink
    
    def run(self, spark: SparkSession) -> None:
        """Executa o pipeline completo."""
        # Extract
        df = self.source.read(spark)
        
        # Validate
        df = self._validate_schema(df)
        
        # Transform
        df = self._transform(df)
        
        # Load
        self.sink.write(df)
    
    def _validate_schema(self, df: DataFrame) -> DataFrame:
        """Valida schema de entrada."""
        expected_schema = StructType([
            StructField("venda_id", IntegerType(), False),
            StructField("cliente_id", IntegerType(), False),
            StructField("produto_id", IntegerType(), False),
            StructField("valor", IntegerType(), False),
            StructField("data_venda", TimestampType(), False),
        ])
        
        # Verificar colunas obrigatórias
        for field in expected_schema.fields:
            if field.name not in df.columns:
                raise ValueError(f"Coluna obrigatória ausente: {field.name}")
        
        return df.select([field.name for field in expected_schema.fields])
    
    def _transform(self, df: DataFrame) -> DataFrame:
        """Aplica transformações de negócio."""
        # Filtrar vendas válidas (valor > 0)
        df = df.filter(F.col("valor") > 0)
        
        # Adicionar coluna de ano/mês para particionamento
        df = df.withColumn("ano", F.year("data_venda"))
        df = df.withColumn("mes", F.month("data_venda"))
        
        # Calcular métricas agregadas (se necessário)
        # df = self._calculate_metrics(df)
        
        return df

# Implementações concretas
class HDFSSource:
    """Lê dados do HDFS."""
    
    def __init__(self, path: str, format: str = "parquet"):
        self.path = path
        self.format = format
    
    def read(self, spark: SparkSession) -> DataFrame:
        return spark.read.format(self.format).load(self.path)

class HDFSSink:
    """Escreve dados no HDFS."""
    
    def __init__(self, path: str, partition_by: list[str] = None):
        self.path = path
        self.partition_by = partition_by or []
    
    def write(self, df: DataFrame) -> None:
        writer = df.write.mode("overwrite").format("parquet")
        
        if self.partition_by:
            writer = writer.partitionBy(*self.partition_by)
        
        writer.save(self.path)
```

## Performance: Otimizações Obrigatórias

### 1. NUNCA `.collect()` sem amostragem

```python
# ❌ ERRADO
df = spark.read.parquet("hdfs://large_dataset")
results = df.collect()  # BOOM! OOM no driver

# ✅ CORRETO
df = spark.read.parquet("hdfs://large_dataset")
sample = df.limit(100).collect()  # ou .sample(0.01)
```

### 2. Broadcast joins para tabelas pequenas

```python
from pyspark.sql.functions import broadcast

# ❌ ERRADO — shuffle massivo
large_df = spark.read.parquet("hdfs://vendas")  # 1B linhas
small_df = spark.read.parquet("hdfs://produtos")  # 1K linhas
result = large_df.join(small_df, "produto_id")

# ✅ CORRETO — sem shuffle
result = large_df.join(broadcast(small_df), "produto_id")
```

### 3. Particionar antes de joins custosos

```python
# ❌ ERRADO
df1 = spark.read.parquet("hdfs://vendas")
df2 = spark.read.parquet("hdfs://clientes")
result = df1.join(df2, "cliente_id")  # shuffle desbalanceado

# ✅ CORRETO
df1 = spark.read.parquet("hdfs://vendas").repartition(200, "cliente_id")
df2 = spark.read.parquet("hdfs://clientes").repartition(200, "cliente_id")
result = df1.join(df2, "cliente_id")  # shuffle balanceado
```

### 4. Persist/Cache datasets reutilizados

```python
# ❌ ERRADO — lê HDFS múltiplas vezes
df = spark.read.parquet("hdfs://vendas")
count = df.count()
total = df.agg({"valor": "sum"}).collect()[0][0]
avg = df.agg({"valor": "avg"}).collect()[0][0]

# ✅ CORRETO — lê HDFS uma vez
df = spark.read.parquet("hdfs://vendas").cache()
count = df.count()  # materializa cache
total = df.agg({"valor": "sum"}).collect()[0][0]  # usa cache
avg = df.agg({"valor": "avg"}).collect()[0][0]  # usa cache
df.unpersist()  # libera memória ao final
```

### 5. Usar colunas particionadas em filtros

```python
# ❌ ERRADO — lê todas partições
df = spark.read.parquet("hdfs://vendas")  # particionado por ano/mes
result = df.filter(F.col("data_venda") >= "2024-01-01")

# ✅ CORRETO — lê apenas partições necessárias
df = spark.read.parquet("hdfs://vendas")
result = df.filter((F.col("ano") == 2024) & (F.col("mes") >= 1))
```

## Integração com Airflow

```python
# dags/etl_vendas_dag.py
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['data-team@example.com'],
}

with DAG(
    'etl_vendas',
    default_args=default_args,
    description='ETL diário de vendas',
    schedule_interval='0 2 * * *',  # 2h da manhã
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['vendas', 'etl', 'pyspark'],
) as dag:
    
    extract_vendas = SparkSubmitOperator(
        task_id='extract_vendas',
        application='/opt/jobs/etl_vendas.py',
        name='etl_vendas',
        conn_id='spark_default',
        conf={
            'spark.executor.memory': '4g',
            'spark.executor.cores': '2',
            'spark.dynamicAllocation.enabled': 'true',
            'spark.sql.shuffle.partitions': '200',
        },
        application_args=[
            '--input', 'hdfs://vendas_raw/{{ ds }}',
            '--output', 'hdfs://vendas_processadas/{{ ds }}',
        ],
    )
    
    validate_output = SparkSubmitOperator(
        task_id='validate_output',
        application='/opt/jobs/validate_vendas.py',
        name='validate_vendas',
        conn_id='spark_default',
        application_args=[
            '--path', 'hdfs://vendas_processadas/{{ ds }}',
            '--min-rows', '1000',
        ],
    )
    
    extract_vendas >> validate_output
```

## Testes

```python
# tests/test_vendas_pipeline.py
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType
from datetime import datetime
from jobs.etl_vendas import VendasPipeline

@pytest.fixture(scope="session")
def spark():
    """Cria SparkSession para testes."""
    return SparkSession.builder \
        .master("local[2]") \
        .appName("test") \
        .getOrCreate()

def test_transform_filters_invalid_values(spark):
    """Testa que valores inválidos são filtrados."""
    # Arrange
    schema = StructType([
        StructField("venda_id", IntegerType(), False),
        StructField("cliente_id", IntegerType(), False),
        StructField("produto_id", IntegerType(), False),
        StructField("valor", IntegerType(), False),
        StructField("data_venda", TimestampType(), False),
    ])
    
    data = [
        (1, 100, 200, 1000, datetime(2024, 1, 1)),
        (2, 101, 201, 0, datetime(2024, 1, 2)),  # valor inválido
        (3, 102, 202, -500, datetime(2024, 1, 3)),  # valor inválido
        (4, 103, 203, 2000, datetime(2024, 1, 4)),
    ]
    
    df = spark.createDataFrame(data, schema)
    
    # Act
    pipeline = VendasPipeline(None, None)
    result = pipeline._transform(df)
    
    # Assert
    assert result.count() == 2  # apenas 2 válidas
    assert all(row.valor > 0 for row in result.collect())

def test_validate_schema_raises_on_missing_column(spark):
    """Testa que schema inválido levanta erro."""
    # Arrange
    df = spark.createDataFrame([(1, 100)], ["venda_id", "cliente_id"])
    
    # Act & Assert
    pipeline = VendasPipeline(None, None)
    with pytest.raises(ValueError, match="Coluna obrigatória ausente"):
        pipeline._validate_schema(df)
```

## Logging e Métricas

```python
import logging
from pyspark.sql import DataFrame

logger = logging.getLogger(__name__)

def log_dataframe_metrics(df: DataFrame, stage: str) -> None:
    """Registra métricas de um DataFrame."""
    count = df.count()
    partitions = df.rdd.getNumPartitions()
    
    logger.info(
        f"[{stage}] Linhas: {count:,} | Partições: {partitions}"
    )
    
    # Exemplo de uso
    df = spark.read.parquet("hdfs://input")
    log_dataframe_metrics(df, "input")
    
    df = transform(df)
    log_dataframe_metrics(df, "after_transform")
```

## Checklist de Qualidade

```
[ ] Schema validado na entrada
[ ] Sem .collect() em datasets grandes
[ ] Broadcast joins para tabelas < 200MB
[ ] Particionamento adequado (200-2000 partições)
[ ] Cache/persist apenas quando necessário (e unpersist ao final)
[ ] Logging de métricas (linhas entrada/saída/descartadas)
[ ] Testes com fixtures sintéticos
[ ] DAG Airflow idempotente
[ ] Tratamento de erros e retries configurados
[ ] Documentação de particionamento de saída
```

## Referências

- [PySpark Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Airflow Spark Integration](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/index.html)
