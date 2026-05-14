---
description: Audita o código Django atual para N+1 queries e sugere otimizações
---

Analise todo o código Django neste projeto para identificar problemas de N+1 queries.

Para cada problema encontrado:

1. Mostre o código problemático com número de linha
2. Explique por que é um N+1
3. Mostre a correção com select_related ou prefetch_related
4. Estime o impacto em número de queries economizadas

Padrões a buscar:

- Loop sobre queryset com acesso a FK dentro do loop
- `Model.objects.all()` sem select_related quando há FKs usadas no template/serializer
- `related_manager.all()` dentro de loop (ManyToMany sem prefetch)
- Serializers DRF sem `select_related` nas queries de queryset
- Celery tasks que iteram sobre objetos com relacionamentos

Após a análise, priorize por:

- ALTO impacto (queries em endpoints críticos ou com muitos registros)
- MÉDIO impacto (endpoints moderados)
- BAIXO impacto (raramente acessados ou poucos registros)
