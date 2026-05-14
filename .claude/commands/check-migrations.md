---
description: Verifica migrations pendentes, conflitos e problemas potenciais
---

Verifique o estado das migrations Django:

## 1. Status Geral

```bash
python manage.py showmigrations
```

Identificar:
- [ ] Migrations pendentes (não aplicadas)
- [ ] Conflitos de merge (múltiplas migrations com mesmo número)
- [ ] Migrations órfãs (sem dependências)

## 2. Validação de Migrations

Para cada migration pendente, verificar:

### Segurança em Produção

**❌ Operações perigosas:**
- `DROP TABLE` / `DROP COLUMN` com dados
- `ALTER COLUMN` que pode truncar dados
- `ADD COLUMN NOT NULL` sem default em tabela populada
- Migrations sem `atomic = False` para operações longas

**✅ Operações seguras:**
- `ADD COLUMN` com default ou nullable
- `CREATE INDEX CONCURRENTLY` (PostgreSQL)
- Migrations atômicas para mudanças simples

### Exemplo de Migration Segura

```python
# ❌ PERIGOSO
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='user',
            name='verified',
            field=models.BooleanField(default=False),
            # ⚠️ Vai travar tabela em tabela grande!
        ),
    ]

# ✅ SEGURO (para tabela grande)
class Migration(migrations.Migration):
    atomic = False  # importante!
    
    operations = [
        # Passo 1: adicionar coluna nullable
        migrations.AddField(
            model_name='user',
            name='verified',
            field=models.BooleanField(null=True),
        ),
        # Passo 2: preencher dados em chunks (via RunPython)
        migrations.RunPython(backfill_verified),
        # Passo 3: tornar NOT NULL em migration separada
    ]
```

## 3. Detecção de Conflitos

Procurar migrations com mesmo número:

```bash
# Exemplo de conflito
apps/users/migrations/
  - 0003_add_field.py
  - 0003_add_column.py  # conflito!
```

**Solução:** usar `python manage.py makemigrations --merge`

## 4. Schema Drift

Comparar schema do banco com models:

```bash
python manage.py makemigrations --dry-run --check
```

Se houver mudanças não commitadas:
- Criar migration
- Ou reverter mudanças no model

## 5. Validação Pré-Deploy

Checklist:
- [ ] Todas as migrations testadas localmente
- [ ] Migrations testadas em cópia do banco de produção
- [ ] Backup do banco antes de aplicar
- [ ] Plano de rollback definido
- [ ] Migrations aplicam rapidamente (< 5min ideal)
- [ ] Sem downtime ou downtime planejado

## Formato de Saída

```markdown
# Migration Check Report

## Status
- Migrations pendentes: [número]
- Conflitos detectados: [número]
- Migrations órfãs: [número]

## Migrations Pendentes

### Seguras para Produção
1. `apps/users/0004_add_index.py`
   - Operação: CREATE INDEX CONCURRENTLY
   - Impacto: Baixo
   - Duração estimada: < 1min

### Requerem Atenção
1. `apps/orders/0005_add_status.py`
   - Operação: ADD COLUMN NOT NULL
   - ⚠️ Problema: Tabela com 10M linhas
   - Solução: Fazer em 3 migrations (nullable → backfill → NOT NULL)

### Perigosas (Revisar)
1. `apps/products/0006_remove_old_field.py`
   - Operação: DROP COLUMN
   - ❌ Problema: Dados serão perdidos
   - Recomendação: Backup antes de aplicar

## Conflitos

[Lista de conflitos encontrados e como resolver]

## Recomendações

1. [ação 1]
2. [ação 2]
```
