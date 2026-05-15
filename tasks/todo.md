# Tarefa: Task Manager App — Multiplataforma

## Objetivo

Gerenciador de tarefas cross-platform (Windows, Linux, Android, iOS) com sync em tempo real,
modo offline-first e retomada de sessão. Critério de aceite: criar tarefa no desktop,
sincronizar automaticamente no mobile, sem perda de dados offline.

## Stack

| Camada   | Tecnologia                      |
|----------|---------------------------------|
| Frontend | Flutter (Dart)                  |
| Backend  | FastAPI + PostgreSQL + Redis    |
| Sync     | REST + WebSocket (realtime)     |
| Auth     | JWT + Refresh Token             |
| Mobile   | Android + iOS via Flutter       |
| Desktop  | Windows + Linux via Flutter     |

## Plano de Implementação

### Fase 1 — Backend Core
- [ ] 1.1 Setup projeto FastAPI + PostgreSQL (Docker Compose local)
- [ ] 1.2 Models: User, Area, Project, Task, Subtask, Tag, TaskHistory
- [ ] 1.3 Auth: registro, login, refresh token, logout
- [ ] 1.4 CRUD Tasks + Projects + Areas (REST API)
- [ ] 1.5 Filtros, busca full-text (PostgreSQL tsvector)
- [ ] 1.6 WebSocket endpoint para sync em tempo real
- [ ] 1.7 Conflict resolution (last-write-wins com timestamp + version)
- [ ] 1.8 Testes unitários e de integração (pytest, coverage ≥ 80%)

### Fase 2 — Flutter App Core
- [ ] 2.1 Setup Flutter + estrutura de pastas (feature-first)
- [ ] 2.2 State management: Riverpod
- [ ] 2.3 Local database: Drift (SQLite) para offline-first
- [ ] 2.4 HTTP client + WebSocket client (Dio + web_socket_channel)
- [ ] 2.5 Auth screens: login, register
- [ ] 2.6 Sync engine: fila de operações locais → push quando online
- [ ] 2.7 Screens: Home/Hoje, Lista, Projeto, Tarefa detalhe

### Fase 3 — Features de Produtividade
- [ ] 3.1 Views: Lista, Kanban, Calendário
- [ ] 3.2 Timer Pomodoro integrado por tarefa
- [ ] 3.3 Modo "Retomada de Sessão" — estado persistido localmente
- [ ] 3.4 Notificações locais (vencimentos, pomodoro)
- [ ] 3.5 Subtarefas (checklist inline)
- [ ] 3.6 Dependências entre tarefas (bloqueia/desbloqueia)
- [ ] 3.7 Recorrência de tarefas

### Fase 4 — Polish e Deploy
- [ ] 4.1 Tema claro/escuro, design system próprio
- [ ] 4.2 Keyboard shortcuts no desktop
- [ ] 4.3 Export: markdown, CSV, JSON
- [ ] 4.4 CI/CD: GitHub Actions (build Flutter, testes backend)
- [ ] 4.5 Deploy backend: Docker + VPS (ou Railway)
- [ ] 4.6 Build desktop: Windows installer + Linux AppImage
- [ ] 4.7 Build mobile: Android APK/AAB, iOS IPA

## Decisões Arquiteturais (ver decisions.md)
- Offline-first com Drift (SQLite) + sync queue
- Conflict resolution: last-write-wins com campo `updated_at` + `version`
- Riverpod para state management (não Bloc/GetX)
- FastAPI sobre Django: menor overhead para API pura + async nativo

## Verificação

- [ ] Testes passando — `pytest -n auto --cov`
- [ ] Lint sem erros — `ruff check . --fix && mypy .` (backend) + `flutter analyze` (app)
- [ ] Sync funcionando offline → online sem perda
- [ ] Retomada de sessão funcional
- [ ] Checklist universal do CLAUDE.md concluída

## Review

[a preencher após conclusão]
