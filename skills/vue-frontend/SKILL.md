---
name: vue-frontend
description: >
  Desenvolver componentes e features Vue.js 3 com TypeScript, Composition API,
  Pinia e Vitest. Usar quando criar ou refatorar componentes Vue, stores, composables,
  ou qualquer código de frontend.
---

# Skill: Vue.js 3 — Frontend

## Stack obrigatória

- Vue 3 | TypeScript | Vite | Pinia | Vue Router
- Testes: Vitest + Vue Test Utils
- Lint: ESLint + Prettier

## Regras fundamentais

- Sempre `<script setup lang="ts">` — nunca Options API em código novo
- TypeScript obrigatório — sem `any` implícito
- Props tipadas com `defineProps<Interface>()` — sem `defineProps({ prop: String })`
- Emits tipados com `defineEmits<{ event: [arg: Type] }>()`
- Composables para lógica reutilizável (prefixo `use`)
- Pinia para estado compartilhado — sem `provide/inject` para estado global

## Template de Componente

```vue

<script setup lang="ts">
  import {ref, computed, onMounted} from 'vue'
  import {useUserStore} from '@/stores/user'

  interface Props {
    userId: number
    readonly?: boolean
  }

  interface Emits {
    save: [userId: number]
    cancel: []
  }

  const props = withDefaults(defineProps<Props>(), {
    readonly: false,
  })

  const emit = defineEmits<Emits>()

  const userStore = useUserStore()
  const isLoading = ref(false)
  const errorMessage = ref<string | null>(null)

  const displayName = computed(() => userStore.getUserById(props.userId)?.name ?? '—')

  async function handleSave(): Promise<void> {
    isLoading.value = true
    errorMessage.value = null
    try {
      await userStore.save(props.userId)
      emit('save', props.userId)
    } catch (error) {
      errorMessage.value = 'Erro ao salvar. Tente novamente.'
      console.error('handleSave falhou:', error)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(async () => {
    await userStore.fetchUser(props.userId)
  })
</script>

<template>
  <div class="user-form">
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <button :disabled="isLoading || props.readonly" @click="handleSave">
      {{ isLoading ? 'Salvando...' : 'Salvar' }}
    </button>
  </div>
</template>
```

## Template de Store (Pinia)

```typescript
import {defineStore} from 'pinia'
import {ref, computed} from 'vue'
import type {User} from '@/types/user'
import {userApi} from '@/api/user'

export const useUserStore = defineStore('user', () => {
    const users = ref<Map<number, User>>(new Map())
    const isLoading = ref(false)

    const getUserById = computed(() => (id: number) => users.value.get(id))

    async function fetchUser(id: number): Promise<void> {
        if (users.value.has(id)) return
        isLoading.value = true
        try {
            const user = await userApi.getById(id)
            users.value.set(id, user)
        } finally {
            isLoading.value = false
        }
    }

    async function save(id: number): Promise<void> {
        const user = users.value.get(id)
        if (!user) throw new Error(`Usuário ${id} não encontrado no store`)
        const updated = await userApi.update(id, user)
        users.value.set(id, updated)
    }

    return {users, isLoading, getUserById, fetchUser, save}
})
```

## Template de Composable

```typescript
// src/composables/useAsync.ts
import {ref} from 'vue'

export function useAsync<T>(fn: () => Promise<T>) {
    const data = ref<T | null>(null)
    const error = ref<Error | null>(null)
    const isLoading = ref(false)

    async function execute(): Promise<void> {
        isLoading.value = true
        error.value = null
        try {
            data.value = await fn()
        } catch (e) {
            error.value = e instanceof Error ? e : new Error(String(e))
        } finally {
            isLoading.value = false
        }
    }

    return {data, error, isLoading, execute}
}
```

## Teste de Componente (Vitest)

```typescript
import {describe, it, expect, vi} from 'vitest'
import {mount} from '@vue/test-utils'
import {createPinia, setActivePinia} from 'pinia'
import UserForm from '@/components/UserForm.vue'

describe('UserForm', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
    })

    it('emite save com o userId correto ao clicar em Salvar', async () => {
        const wrapper = mount(UserForm, {props: {userId: 42}})
        await wrapper.find('button').trigger('click')
        expect(wrapper.emitted('save')).toEqual([[42]])
    })
})
```

## Checklist pré-entrega Vue.js

```
[ ] npm run type-check → sem erros (vue-tsc)
[ ] npm run lint       → sem warnings ou erros
[ ] npm run test:unit  → todos passando
[ ] npm run build      → build sem erros
[ ] Sem `any` explícito no código novo
[ ] Props e emits completamente tipados
[ ] Composables com nome iniciando em `use`
[ ] Estado global somente via Pinia
```
