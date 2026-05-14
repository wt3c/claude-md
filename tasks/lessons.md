# Lições Aprendidas

> Este arquivo registra padrões e antipadrões aprendidos durante o desenvolvimento.  
> Categorizado por stack para fácil referência.

---

## Python / Django

### [PADRÃO] SQLAlchemy engine para Pandas ↔ PostgreSQL

**Contexto:** Evitar UserWarning DBAPI2 ao usar Pandas com Django ORM  
**Solução:** Usar `create_engine()` do SQLAlchemy em vez de conexão direta  
**Quando aplicar:** Sempre que conectar Pandas diretamente ao banco PostgreSQL  
**Código:**
```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host:5432/db")
df = pd.read_sql("SELECT * FROM users", con=engine)
```

### [ANTIPADRÃO] N+1 queries sem select_related

**Problema:** Loop sobre queryset sem prefetch causou timeout em produção  
**Solução:** Sempre usar `.select_related()` para ForeignKey ou `.prefetch_related()` para Many-to-Many  
**Detecção:** Django Debug Toolbar, plugin nplusone  
**Código:**
```python
# ❌ ERRADO
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # Query a cada iteração

# ✅ CORRETO
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)  # Uma query total
```

### [PADRÃO] UV para gerenciamento de pacotes

**Contexto:** pip e poetry são lentos e não reproduzíveis  
**Solução:** Usar `uv` para instalação ultrarrápida e determinística  
**Quando aplicar:** SEMPRE, em todos os projetos Python  
**Código:**
```bash
uv pip install -r requirements.txt  # 10-100x mais rápido que pip
uv venv  # criar venv
uv run pytest  # rodar comando no venv
```

---

## PySpark / Airflow / Hadoop

### [ANTIPADRÃO] .collect() sem amostragem prévia

**Problema:** collect() em dataset de 10M linhas estourou memória do driver (OOM)  
**Solução:** Sempre `.limit()` ou `.sample()` antes de collect() para trazer dados ao driver  
**Quando aplicar:** Qualquer operação que traga dados do cluster para o driver  
**Código:**
```python
# ❌ ERRADO
df = spark.read.parquet("hdfs://large_dataset")
results = df.collect()  # BOOM! OOM

# ✅ CORRETO
df = spark.read.parquet("hdfs://large_dataset")
sample = df.limit(100).collect()  # ou .sample(0.01)
```

### [PADRÃO] Broadcast join para tabelas pequenas

**Contexto:** Join de tabela grande (1B linhas) com tabela pequena (1K linhas) causou shuffle massivo  
**Solução:** Usar `broadcast()` para enviar tabela pequena para todos os executors  
**Quando aplicar:** Joins com tabelas < 200MB  
**Código:**
```python
from pyspark.sql.functions import broadcast

large_df = spark.read.parquet("hdfs://large")
small_df = spark.read.parquet("hdfs://small")
result = large_df.join(broadcast(small_df), "key")  # Sem shuffle
```

### [PADRÃO] Validação de schema em DAGs Airflow

**Contexto:** Pipeline falhou silenciosamente quando schema mudou upstream  
**Solução:** Validar schema de entrada no início de cada task  
**Quando aplicar:** Sempre, em todas as DAGs  
**Código:**
```python
from great_expectations.dataset import SparkDFDataset

def validate_input(df):
    ge_df = SparkDFDataset(df)
    assert ge_df.expect_column_to_exist("user_id")
    assert ge_df.expect_column_values_to_not_be_null("user_id")
    return df
```

---

## C# / Unity (Mobile Android)

### [PADRÃO] ScriptableObjects para configuração

**Contexto:** Evitar hardcode e facilitar tweaking de gameplay sem recompilar  
**Solução:** Criar ScriptableObjects para todos os dados de configuração  
**Quando aplicar:** Qualquer dado que designers precisam ajustar (armas, inimigos, níveis)  
**Código:**
```csharp
[CreateAssetMenu(fileName = "WeaponData", menuName = "Gameplay/Weapon")]
public class WeaponData : ScriptableObject
{
    public string weaponName;
    public int damage;
    public float fireRate;
    public AudioClip fireSound;
}
```

### [ANTIPADRÃO] FindObjectOfType em Update/FixedUpdate

**Problema:** FindObjectOfType a cada frame causou drop de FPS de 60 para 15  
**Solução:** Cachear referência em Awake/Start ou usar injeção via Inspector  
**Quando aplicar:** NUNCA usar Find* em hot paths (Update, FixedUpdate, LateUpdate)  
**Código:**
```csharp
// ❌ ERRADO
void Update() {
    var player = FindObjectOfType<Player>();  // Busca toda a hierarquia
}

// ✅ CORRETO
private Player player;
void Awake() {
    player = FindObjectOfType<Player>();  // Uma vez só
}
void Update() {
    // usar player cacheado
}
```

### [PADRÃO] Object Pooling para projéteis

**Contexto:** Instanciar/destruir 100 projéteis por segundo causou GC spikes  
**Solução:** Implementar Object Pool para reciclagem de GameObjects  
**Quando aplicar:** Entidades com spawn/destroy frequente (projéteis, particles, inimigos)  
**Código:**
```csharp
public class BulletPool : MonoBehaviour
{
    public GameObject bulletPrefab;
    private Queue<GameObject> pool = new Queue<GameObject>();
    
    public GameObject Get() {
        if (pool.Count > 0) return pool.Dequeue();
        return Instantiate(bulletPrefab);
    }
    
    public void Return(GameObject bullet) {
        bullet.SetActive(false);
        pool.Enqueue(bullet);
    }
}
```

---

## GitLab CI/CD

### [PADRÃO] Cache de dependências Python com UV

**Contexto:** Pipeline levava 5min só para instalar dependências a cada run  
**Solução:** Cachear venv criado pelo UV entre builds  
**Quando aplicar:** Todos os pipelines Python  
**Código:**
```yaml
test:
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .venv/
  before_script:
    - pip install uv
    - uv venv
    - uv pip install -r requirements.txt
  script:
    - uv run pytest
```

---

## Vue.js 3

### [PADRÃO] Composables para lógica reutilizável

**Contexto:** Lógica de autenticação duplicada em 5 componentes  
**Solução:** Extrair para composable reutilizável  
**Quando aplicar:** Qualquer lógica compartilhada entre componentes  
**Código:**
```javascript
// composables/useAuth.js
import { ref, computed } from 'vue'

export function useAuth() {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  
  async function login(credentials) {
    const response = await api.post('/login', credentials)
    user.value = response.data.user
  }
  
  return { user, isAuthenticated, login }
}

// Uso em componente
import { useAuth } from '@/composables/useAuth'
const { user, isAuthenticated, login } = useAuth()
```

---

## OpenTelemetry / Dynatrace

### [PADRÃO] Atributos semânticos em spans

**Contexto:** Traces sem contexto dificultaram debugging de latência  
**Solução:** Adicionar atributos semânticos (user_id, order_id, etc.) em todos os spans  
**Quando aplicar:** Todo tracing manual  
**Código:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id: int, user_id: int):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("user.id", user_id)
        span.set_attribute("service.name", "order-service")
        # lógica aqui
```

---

**Atualizar este arquivo sempre que aprender algo novo ou corrigir um erro.**
