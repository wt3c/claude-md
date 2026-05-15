# Architecture Decision Records

---

# ADR-001: UV como gerenciador de pacotes Python

**Status**: Aceito
**Data**: 2026-05-14

## Contexto

Precisamos de um gerenciador de pacotes Python rápido, reproduzível e compatível com pyproject.toml.

## Decisão

Usar UV em todos os projetos Python. Nunca pip diretamente.

## Consequências

- Instalação de dependências 10-100x mais rápida
- Lock file determinístico (uv.lock)
- Compatível com CI/CD via `uv sync`
- Requer instalação do UV nos runners GitLab

---

# ADR-002: Infisical para gestão de secrets

**Status**: Aceito
**Data**: 2026-05-14

## Contexto

Secrets eram gerenciados via arquivos `.env` locais e variáveis GitLab CI, criando riscos de exposição.

## Decisão

Infisical como fonte única de secrets. Machine Identity para CI/CD. CLI para desenvolvimento local.

## Consequências

- Rotação centralizada de secrets
- Auditoria de acesso
- Requer Infisical CLI instalado localmente
- CI/CD precisa de INFISICAL_CLIENT_ID e INFISICAL_CLIENT_SECRET como variáveis masked do GitLab

---

# ADR-003: Protocol-based DI em vez de herança concreta

**Status**: Aceito
**Data**: 2026-05-14

## Contexto

Código Django com lógica de negócio acoplada a implementações concretas dificultava testes e reutilização.

## Decisão

Usar `typing.Protocol` para definir interfaces de Repository e Service. Injetar dependências via construtor.

## Consequências

- Testabilidade alta (fácil mockar protocols)
- Sem herança múltipla ou acoplamento a Django ORM em services
- Curva de aprendizado inicial para o time
- Necessidade de type checking (mypy) para garantir conformidade

---

# ADR-004: Task Manager — Stack Flutter + FastAPI

**Status**: Aceito
**Data**: 2026-05-15

## Contexto

Gerenciador de tarefas multiplataforma (Windows, Linux, Android, iOS) com offline-first e sync em tempo real.
Avaliadas 3 opções de frontend: Flutter, Tauri+Vue, React Native+Expo.

## Decisão

- **Frontend**: Flutter — único com suporte maduro em todas as 4 plataformas com 1 codebase
- **Backend**: FastAPI + PostgreSQL + Redis — async nativo, menor overhead que Django para API pura
- **State**: Riverpod — mais tipado e testável que Bloc/GetX/Provider
- **Local DB**: Drift (SQLite) — offline-first, type-safe, sync queue integrada
- **Sync**: last-write-wins via `updated_at` + `version` inteiro — simples e suficiente para uso pessoal
- **Realtime**: WebSocket para push de mudanças entre dispositivos
- **Auth**: JWT (access 15min) + Refresh Token (30d, rotativo)

## Consequências

- Dart é necessário (curva se não conhecia antes)
- Tauri descartado: mobile ainda experimental na v2
- React Native descartado: Electron pesado para desktop
- FastAPI vs Django: sem admin out-of-the-box (aceitável para API pura)
- Conflict resolution simples (last-write-wins) pode perder edições simultâneas — aceitável para uso pessoal/pequeno time

---

<!-- Template para novos ADRs:

# ADR-NNN: [título]

**Status**: Proposto | Aceito | Depreciado
**Data**: YYYY-MM-DD

## Contexto
[Por que esta decisão foi necessária?]

## Decisão
[O que foi decidido?]

## Consequências
[Quais são os trade-offs? O que fica mais fácil? O que fica mais difícil?]

-->
