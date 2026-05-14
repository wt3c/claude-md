---
description: Analisa código Django para N+1 queries e sugere otimizações
---

Analise o código Django atual para detectar N+1 queries:

## Escaneamento

1. **Views e ViewSets**
   - Identificar loops sobre querysets
   - Verificar acesso a related objects dentro de loops
   - Verificar serializers acessando relações

2. **Serializers (DRF)**
   - Nested serializers sem prefetch configurado
   - Métodos serializados acessando ForeignKey/ManyToMany

3. **Templates**
   - Loops em templates acessando relações

## Detecção

Procurar padrões como:

```python
# ❌ N+1 Query
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # query a cada iteração

# ❌ N+1 em Serializer
class UserSerializer(serializers.ModelSerializer):
    profile_bio = serializers.CharField(source='profile.bio')  # N+1

# ❌ N+1 em Template
{% for user in users %}
    {{ user.profile.bio }}  <!-- query a cada iteração -->
{% endfor %}
```

## Soluções

Sugerir correções usando:

- **select_related()** para ForeignKey (OneToOne)
- **prefetch_related()** para ManyToMany (reverse ForeignKey)
- **Prefetch** objects para queries customizadas

```python
# ✅ Corrigido
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)  # uma query total

# ✅ Serializer otimizado
class UserViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return User.objects.select_related('profile')

# ✅ Prefetch customizado
from django.db.models import Prefetch

users = User.objects.prefetch_related(
    Prefetch('orders', queryset=Order.objects.filter(status='active'))
)
```

## Ferramentas Recomendadas

- Django Debug Toolbar (development)
- django-silk (profiling)
- nplusone (detection automática)

## Formato de Saída

```markdown
# N+1 Query Audit

## Problemas Encontrados

### Crítico (N+1 em produção)
1. [arquivo:linha] - [descrição]
   - Solução: [código sugerido]

### Atenção (potencial N+1)
1. [arquivo:linha] - [descrição]
   - Solução: [código sugerido]

## Código Otimizado

[Exemplos de código corrigido]

## Impacto Estimado

- Redução de queries: [N queries → M queries]
- Performance: [estimativa de melhoria]
```
