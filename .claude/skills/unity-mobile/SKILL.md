---
name: unity-mobile
description: >
  Desenvolver jogos Unity para mobile Android com performance otimizada,
  TDD, e boas práticas de arquitetura. Usar quando criar features de gameplay,
  otimizar performance, ou estruturar código Unity.
---

# Unity Mobile (Android) Pattern

## Quando aplicar

Esta skill deve ser usada quando:
- Criar nova feature de gameplay para mobile Android
- Refatorar código Unity existente
- Otimizar performance (FPS, memória, tamanho de build)
- Configurar build para Google Play
- Escrever testes para lógica de jogo

## Build Settings Obrigatórios

```
Player Settings → Other Settings:
  - Scripting Backend: IL2CPP (não Mono)
  - Target Architectures: ARM64 ✓ (ARMv7 desabilitado)
  - API Level: Android 12 (API 31) mínimo
  
Player Settings → Graphics:
  - Graphics API: Vulkan (primeiro), OpenGLES3 (fallback)
  - Color Space: Linear
  
Universal Render Pipeline (URP):
  - Quality: Medium (para devices mid-range)
  - MSAA: 2x ou desabilitado (depende do target)
  - Shadow Resolution: 1024 (ajustar conforme necessário)
```

## Arquitetura: MVC/MVP

### Model (Dados + Lógica de Negócio)

```csharp
// Models/Player.cs
using System;

[Serializable]
public class Player
{
    public int health;
    public int maxHealth;
    public float moveSpeed;
    
    public Player(int maxHealth, float moveSpeed)
    {
        this.maxHealth = maxHealth;
        this.health = maxHealth;
        this.moveSpeed = moveSpeed;
    }
    
    public void TakeDamage(int damage)
    {
        health = Math.Max(0, health - damage);
    }
    
    public void Heal(int amount)
    {
        health = Math.Min(maxHealth, health + amount);
    }
    
    public bool IsAlive => health > 0;
}
```

### View (MonoBehaviour — apenas apresentação)

```csharp
// Views/PlayerView.cs
using UnityEngine;
using UnityEngine.UI;

public class PlayerView : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private Slider healthBar;
    [SerializeField] private Text healthText;
    [SerializeField] private Animator animator;
    
    public void UpdateHealth(int current, int max)
    {
        healthBar.value = (float)current / max;
        healthText.text = $"{current} / {max}";
    }
    
    public void PlayHitAnimation()
    {
        animator.SetTrigger("Hit");
    }
    
    public void PlayDeathAnimation()
    {
        animator.SetTrigger("Death");
    }
}
```

### Presenter (Orquestração)

```csharp
// Presenters/PlayerPresenter.cs
using UnityEngine;

public class PlayerPresenter : MonoBehaviour
{
    [Header("Configuration")]
    [SerializeField] private PlayerData playerData;  // ScriptableObject
    
    [Header("View")]
    [SerializeField] private PlayerView view;
    
    private Player model;
    
    private void Awake()
    {
        model = new Player(
            maxHealth: playerData.maxHealth,
            moveSpeed: playerData.moveSpeed
        );
    }
    
    private void Start()
    {
        UpdateView();
    }
    
    public void OnTakeDamage(int damage)
    {
        model.TakeDamage(damage);
        view.PlayHitAnimation();
        UpdateView();
        
        if (!model.IsAlive)
        {
            OnDeath();
        }
    }
    
    public void OnHeal(int amount)
    {
        model.Heal(amount);
        UpdateView();
    }
    
    private void OnDeath()
    {
        view.PlayDeathAnimation();
        // Lógica adicional (game over, etc.)
    }
    
    private void UpdateView()
    {
        view.UpdateHealth(model.health, model.maxHealth);
    }
}
```

## ScriptableObjects para Configuração

```csharp
// Data/PlayerData.cs
using UnityEngine;

[CreateAssetMenu(fileName = "PlayerData", menuName = "Game/Player Data")]
public class PlayerData : ScriptableObject
{
    [Header("Stats")]
    public int maxHealth = 100;
    public float moveSpeed = 5f;
    public int damage = 10;
    
    [Header("Audio")]
    public AudioClip hitSound;
    public AudioClip deathSound;
    
    [Header("VFX")]
    public GameObject hitEffect;
    public GameObject deathEffect;
}
```

## Object Pooling (Obrigatório para spawns frequentes)

```csharp
// Pooling/ObjectPool.cs
using System.Collections.Generic;
using UnityEngine;

public class ObjectPool : MonoBehaviour
{
    [SerializeField] private GameObject prefab;
    [SerializeField] private int initialSize = 10;
    [SerializeField] private int maxSize = 100;
    
    private Queue<GameObject> pool = new Queue<GameObject>();
    private HashSet<GameObject> active = new HashSet<GameObject>();
    
    private void Awake()
    {
        for (int i = 0; i < initialSize; i++)
        {
            CreateNewObject();
        }
    }
    
    public GameObject Get()
    {
        GameObject obj;
        
        if (pool.Count > 0)
        {
            obj = pool.Dequeue();
        }
        else if (active.Count < maxSize)
        {
            obj = CreateNewObject();
        }
        else
        {
            Debug.LogWarning($"Pool limit reached: {maxSize}");
            return null;
        }
        
        obj.SetActive(true);
        active.Add(obj);
        return obj;
    }
    
    public void Return(GameObject obj)
    {
        if (!active.Contains(obj))
        {
            Debug.LogWarning("Trying to return object not from this pool");
            return;
        }
        
        obj.SetActive(false);
        active.Remove(obj);
        pool.Enqueue(obj);
    }
    
    private GameObject CreateNewObject()
    {
        var obj = Instantiate(prefab, transform);
        obj.SetActive(false);
        pool.Enqueue(obj);
        return obj;
    }
}

// Uso
public class BulletSpawner : MonoBehaviour
{
    [SerializeField] private ObjectPool bulletPool;
    
    public void Fire()
    {
        var bullet = bulletPool.Get();
        if (bullet != null)
        {
            bullet.transform.position = transform.position;
            // configurar velocidade, etc.
        }
    }
}
```

## Testes com Unity Test Framework

### Edit Mode Tests (lógica pura)

```csharp
// Tests/EditMode/PlayerTests.cs
using NUnit.Framework;

public class PlayerTests
{
    [Test]
    public void TakeDamage_ReducesHealth()
    {
        // Arrange
        var player = new Player(maxHealth: 100, moveSpeed: 5f);
        
        // Act
        player.TakeDamage(30);
        
        // Assert
        Assert.AreEqual(70, player.health);
    }
    
    [Test]
    public void TakeDamage_DoesNotGoBelowZero()
    {
        // Arrange
        var player = new Player(maxHealth: 100, moveSpeed: 5f);
        
        // Act
        player.TakeDamage(150);
        
        // Assert
        Assert.AreEqual(0, player.health);
    }
    
    [Test]
    public void Heal_IncreasesHealth()
    {
        // Arrange
        var player = new Player(maxHealth: 100, moveSpeed: 5f);
        player.TakeDamage(50);
        
        // Act
        player.Heal(30);
        
        // Assert
        Assert.AreEqual(80, player.health);
    }
    
    [Test]
    public void Heal_DoesNotExceedMaxHealth()
    {
        // Arrange
        var player = new Player(maxHealth: 100, moveSpeed: 5f);
        player.TakeDamage(20);
        
        // Act
        player.Heal(50);
        
        // Assert
        Assert.AreEqual(100, player.health);
    }
    
    [Test]
    public void IsAlive_ReturnsFalseWhenHealthZero()
    {
        // Arrange
        var player = new Player(maxHealth: 100, moveSpeed: 5f);
        
        // Act
        player.TakeDamage(100);
        
        // Assert
        Assert.IsFalse(player.IsAlive);
    }
}
```

### Play Mode Tests (integração)

```csharp
// Tests/PlayMode/PlayerIntegrationTests.cs
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class PlayerIntegrationTests
{
    [UnityTest]
    public IEnumerator Player_TakeDamage_UpdatesHealthBar()
    {
        // Arrange
        var playerPrefab = Resources.Load<GameObject>("Player");
        var player = Object.Instantiate(playerPrefab);
        var presenter = player.GetComponent<PlayerPresenter>();
        
        yield return null;  // espera 1 frame
        
        // Act
        presenter.OnTakeDamage(30);
        yield return null;
        
        // Assert
        var view = player.GetComponent<PlayerView>();
        Assert.Less(view.GetHealthBarValue(), 1f);
        
        // Cleanup
        Object.Destroy(player);
    }
}
```

## Performance: Evitar GC Allocations

```csharp
// ❌ ERRADO — aloca GC a cada frame
void Update()
{
    var enemies = FindObjectsOfType<Enemy>();  // GC allocation
    foreach (var enemy in enemies)
    {
        // processar
    }
}

// ✅ CORRETO — cachear referências
private List<Enemy> enemies = new List<Enemy>();

void Awake()
{
    enemies.AddRange(FindObjectsOfType<Enemy>());
}

void Update()
{
    foreach (var enemy in enemies)  // sem GC allocation
    {
        // processar
    }
}

// ✅ MELHOR — evitar FindObjectsOfType completamente
[SerializeField] private List<Enemy> enemies;  // injetar via Inspector
```

## Otimizações Mobile

### 1. Texture Compression

```
Import Settings:
  - Format: ASTC (melhor compressão/qualidade)
  - Max Size: 2048 (ou menor se possível)
  - Compression: High Quality
  - Generate Mip Maps: ✓ (para objetos 3D)
```

### 2. Audio Compression

```
Import Settings:
  - Load Type: Compressed in Memory (músicas)
  - Load Type: Decompress on Load (SFX curtos)
  - Compression Format: Vorbis
  - Quality: 50-70% (ajustar por ouvido)
```

### 3. Occlusion Culling

```csharp
// Bake Occlusion Data para cenários grandes
Window → Rendering → Occlusion Culling
  - Smallest Occluder: 5
  - Smallest Hole: 0.25
  - Backface Threshold: 100
```

### 4. LOD (Level of Detail)

```csharp
// Para modelos 3D complexos
GameObject → Add Component → LOD Group
  - LOD 0 (0-60%): modelo completo
  - LOD 1 (60-30%): modelo simplificado
  - LOD 2 (30-0%): modelo muito simplificado ou billboard
```

## Checklist de Build Android

```
[ ] IL2CPP + ARM64 configurado
[ ] Scripting Define Symbols corretos (ex: UNITY_ANDROID)
[ ] Permissions mínimas (apenas necessárias)
[ ] Keystore configurado (release build)
[ ] Version Code incrementado
[ ] Tamanho APK/AAB < 150MB (ou limite do projeto)
[ ] Profiler: sem GC allocations em hot paths
[ ] Profiler: 60 FPS em device mid-range
[ ] Console sem erros (warnings justificados)
[ ] Edit Mode Tests: passando
[ ] Play Mode Tests: passando
[ ] Build testada em device físico
```

## Antipadrões a Evitar

```csharp
// ❌ Singletons estáticos
public class GameManager : MonoBehaviour
{
    public static GameManager Instance;  // dificulta testes
}

// ✅ Injeção via Inspector ou ScriptableObject Events
[SerializeField] private GameManager gameManager;

// ❌ FindObjectOfType em Update
void Update()
{
    var player = FindObjectOfType<Player>();  // lento!
}

// ✅ Cachear em Awake/Start
private Player player;
void Awake()
{
    player = FindObjectOfType<Player>();
}

// ❌ String concatenation em loops
for (int i = 0; i < 1000; i++)
{
    Debug.Log("Enemy " + i);  // GC allocation
}

// ✅ StringBuilder ou evitar logs em production
#if UNITY_EDITOR
    Debug.Log($"Enemy {i}");  // apenas no editor
#endif
```

## Referências

- [Unity Performance Optimization](https://docs.unity3d.com/Manual/MobileOptimizationPracticalGuide.html)
- [URP Best Practices](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@latest)
- [Unity Test Framework](https://docs.unity3d.com/Packages/com.unity.test-framework@latest)
