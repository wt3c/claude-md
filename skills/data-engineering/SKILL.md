---
name: data-engineering
description: >
  Desenvolver pipelines de dados com PySpark, DAGs Airflow e integração Hadoop.
  Usar quando criar ou refatorar jobs PySpark, DAGs, transformações de dados ou
  qualquer código de engenharia de dados.
---

# Skill: Engenharia de Dados — PySpark / Airflow / Hadoop

## Stack

- PySpark 3.x | Apache Airflow 2.x | Hadoop (HDFS/YARN)
- Python 3.12 | UV | Pytest (fixtures, nunca dados reais)

## Regras críticas PySpark

```python
# NUNCA — estoura memória do driver em datasets grandes
df.collect()
df.toPandas()

# CORRETO — amostragem antes
sample = df.sample(fraction=0.01, seed=42).collect()
sample_pd = df.limit(1000).toPandas()

# NUNCA — sem cache em pipeline multi-etapa com reuso
count = df.count()  # recalcula toda a cadeia
df2 = df.filter(...).count()  # recalcula desde o início

# CORRETO — cache quando o DataFrame é reutilizado
df.cache()
count = df.count()
df2 = df.filter(...)
```

## Validação de Schema (obrigatória)

```python
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField, StringType, LongType

EXPECTED_SCHEMA = StructType([
    StructField("id", LongType(), nullable=False),
    StructField("name", StringType(), nullable=True),
    StructField("created_at", StringType(), nullable=False),
])


def validate_schema(df: DataFrame, expected: StructType) -> None:
    """Valida schema antes de qualquer transformação — falha rápido."""
    actual_fields = {f.name: f.dataType for f in df.schema.fields}
    for field in expected.fields:
        if field.name not in actual_fields:
            raise ValueError(f"Campo ausente: {field.name}")
        if type(actual_fields[field.name]) != type(field.dataType):
            raise ValueError(
                f"Tipo incorreto para {field.name}: "
                f"esperado {field.dataType}, encontrado {actual_fields[field.name]}"
            )
```

## Particionamento

```python
# SEMPRE particionar antes de joins custosos
df_grande = df_grande.repartition("data_particao", "regiao")

# SEMPRE particionamento na escrita
df_resultado.write
.partitionBy("ano", "mes")
.mode("overwrite")
.parquet("hdfs:///dados/saida/")
```

## Logging obrigatório por etapa

```python
import logging

logger = logging.getLogger(__name__)


def transform_step(df: DataFrame, step_name: str) -> DataFrame:
    count_in = df.count()
    result = _apply_transformation(df)
    count_out = result.count()
    discarded = count_in - count_out
    logger.info(
        "[%s] entrada=%d saída=%d descartados=%d",
        step_name, count_in, count_out, discarded
    )
    return result
```

## DAG Airflow — Padrão

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
    "email_on_failure": True,
}

with DAG(
        dag_id="pipeline_exemplo",
        default_args=DEFAULT_ARGS,
        start_date=datetime(2026, 1, 1),
        schedule_interval="0 6 * * *",
        catchup=False,  # idempotente: não reprocessar datas antigas
        tags=["producao", "dados"],
) as dag:
    def extrair(**context) -> None:
        # lógica de extração
        # SEMPRE idempotente: rodar 2x = mesmo resultado
        pass


    extrair_task = PythonOperator(
        task_id="extrair",
        python_callable=extrair,
    )
```

### Idempotência — Regras

- Toda DAG deve poder rodar múltiplas vezes com o mesmo resultado
- Usar `execution_date` para delimitar janelas de dados
- Saída em HDFS: `mode("overwrite")` — nunca `append` sem controle de duplicatas
- Alertas explícitos para dados vazios (vazios ≠ erro automático)

## SQLAlchemy para Pandas ↔ Banco

```python
from sqlalchemy import create_engine
import pandas as pd
import os

# NUNCA: pd.read_sql(..., con=conexao_dbapi2)  — UserWarning DBAPI2
# CORRETO: sempre engine SQLAlchemy
engine = create_engine(os.environ["DATABASE_URL"])

df = pd.read_sql("SELECT * FROM tabela WHERE data >= %(data)s", engine, params={"data": "2026-01-01"})
df.to_sql("tabela_destino", engine, if_exists="append", index=False, method="multi")
```

## Teste de Pipeline

```python
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    return SparkSession.builder
    .master("local[2]")
    .appName("test")
    .getOrCreate()


def test_transformacao(spark: SparkSession) -> None:
    # SEMPRE usar dados sintéticos em testes — nunca dados reais
    input_data = [(1, "Alice"), (2, "Bob")]
    df = spark.createDataFrame(input_data, ["id", "nome"])

    resultado = minha_transformacao(df)

    assert resultado.count() == 2
    assert "nome_upper" in resultado.columns
```

## Checklist pré-entrega

```
[ ] Nenhum .collect() sem amostragem prévia em código de produção
[ ] Schema validado no início de cada job
[ ] Particionamento definido e documentado
[ ] Log de entrada/saída/descartados por etapa
[ ] DAG idempotente (rodar 2x = mesmo resultado)
[ ] Testes com fixtures sintéticas (sem dados de produção)
[ ] Alertas para dados vazios configurados
[ ] SQLAlchemy engine (não DBAPI2) para Pandas
```
