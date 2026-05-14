---
name: unity-android
description: >
  Desenvolver jogos e apps mobile Android com Unity + C#, aplicando TDD com
  Unity Test Framework, URP, IL2CPP ARM64 e padrões arquiteturais sem singletons.
  Usar quando criar ou refatorar qualquer código Unity/C#.
---

# Skill: C# / Unity — Mobile Android

## Stack

- Unity (versão LTS atual) | C# | URP | IL2CPP + ARM64
- Testes: Unity Test Framework (Edit Mode + Play Mode)
- Build target: Android (ARM64 obrigatório)

## Regras obrigatórias

### Arquitetura

- **Sem singletons estáticos** → referências diretas ou UnityEvents
- **ScriptableObjects** para todas as configurações (zero hardcode)
- **Separar lógica de jogo da apresentação** — padrão MVC/MVP
- **Object Pooling** para entidades com spawn frequente
- **Sem `FindObjectOfType`** em runtime → injeção via Inspector

### Performance

- Sem alocações GC em hot paths (Update, FixedUpdate, loops críticos)
- Usar `struct` para dados de alta frequência
- Pool de strings para UI dinâmica (StringBuilder)
- Profiler obrigatório antes de marcar como concluído

## Padrão MVC para GameObjects

```csharp
// Model — dados puros, sem herança de MonoBehaviour
[System.Serializable]
public class PlayerData
{
    public int Health;
    public int MaxHealth;
    public float Speed;

    public bool IsAlive => Health > 0;
}

// View — apenas apresentação, sem lógica de jogo
public class PlayerView : MonoBehaviour
{
    [SerializeField] private Slider _healthBar;
    [SerializeField] private Animator _animator;

    public void UpdateHealth(int current, int max)
    {
        _healthBar.value = (float)current / max;
        _animator.SetBool("IsDead", current <= 0);
    }
}

// Controller — orquestra Model e View, recebe input
public class PlayerController : MonoBehaviour
{
    [SerializeField] private PlayerView _view;
    [SerializeField] private PlayerStatsSO _stats;  // ScriptableObject

    private PlayerData _data;

    private void Awake()
    {
        _data = new PlayerData
        {
            MaxHealth = _stats.MaxHealth,
            Health = _stats.MaxHealth,
            Speed = _stats.Speed,
        };
    }

    public void TakeDamage(int amount)
    {
        _data.Health = Mathf.Max(0, _data.Health - amount);
        _view.UpdateHealth(_data.Health, _data.MaxHealth);
    }
}
```

## ScriptableObject para Configuração

```csharp
[CreateAssetMenu(fileName = "PlayerStats", menuName = "Config/PlayerStats")]
public class PlayerStatsSO : ScriptableObject
{
    [field: SerializeField] public int MaxHealth { get; private set; } = 100;
    [field: SerializeField] public float Speed { get; private set; } = 5f;
    [field: SerializeField] public int AttackDamage { get; private set; } = 10;
}
```

## Object Pool

```csharp
public class BulletPool : MonoBehaviour
{
    [SerializeField] private Bullet _prefab;
    [SerializeField] private int _initialSize = 20;

    private readonly Queue<Bullet> _pool = new();

    private void Awake()
    {
        for (int i = 0; i < _initialSize; i++)
            _pool.Enqueue(CreateBullet());
    }

    public Bullet Get()
    {
        var bullet = _pool.Count > 0 ? _pool.Dequeue() : CreateBullet();
        bullet.gameObject.SetActive(true);
        return bullet;
    }

    public void Return(Bullet bullet)
    {
        bullet.gameObject.SetActive(false);
        _pool.Enqueue(bullet);
    }

    private Bullet CreateBullet()
    {
        var b = Instantiate(_prefab, transform);
        b.gameObject.SetActive(false);
        b.SetPool(this);
        return b;
    }
}
```

## Testes (Unity Test Framework)

```csharp
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

// Edit Mode — lógica pura (sem MonoBehaviour ativo)
[TestFixture]
public class PlayerDataTests
{
    [Test]
    public void TakeDamage_ReducesHealth()
    {
        var data = new PlayerData { Health = 100, MaxHealth = 100 };
        data.Health -= 30;
        Assert.AreEqual(70, data.Health);
    }

    [Test]
    public void IsAlive_ReturnsFalse_WhenHealthIsZero()
    {
        var data = new PlayerData { Health = 0, MaxHealth = 100 };
        Assert.IsFalse(data.IsAlive);
    }
}

// Play Mode — integração com engine
public class PlayerControllerTests
{
    [UnityTest]
    public System.Collections.IEnumerator TakeDamage_UpdatesView()
    {
        var go = new GameObject();
        var controller = go.AddComponent<PlayerController>();
        // setup ...
        yield return null;

        controller.TakeDamage(30);

        // assert view state
        Object.Destroy(go);
    }
}
```

## Checklist de Build Android

```
[ ] Unity Test Framework: Edit Mode passando
[ ] Unity Test Framework: Play Mode passando
[ ] Console sem erros (warnings revisados e justificados individualmente)
[ ] Profiler: sem alocações GC em Update/FixedUpdate de objetos críticos
[ ] Build IL2CPP + ARM64 habilitado em Player Settings
[ ] Build testada em device físico Android (não apenas emulador)
[ ] Tamanho APK/AAB verificado e dentro do limite do projeto
[ ] Nenhum FindObjectOfType em runtime
[ ] Nenhum singleton estático em código novo
[ ] ScriptableObjects para todas as configurações tunable
```
