# Lições Aprendidas

## Python / Django

- [PADRÃO] Usar SQLAlchemy engine para Pandas ↔ banco (evita UserWarning DBAPI2)
- [PADRÃO] UV para todos os projetos Python — nunca pip direto
- [PADRÃO] `from secretsloader import load_secrets; load_secrets()` no topo do settings — injeta todos os secrets do Infisical no os.environ via .env de conexão
- [ANTIPADRÃO] Usar `infisical-sdk` diretamente — usar a lib `secretsloader` do MPRJ
- [ANTIPADRÃO] `Model.objects.all()` sem select_related quando há FKs acessadas — causa N+1
- [ANTIPADRÃO] Lógica de negócio em views — mover para services

## PySpark / Dados

- [ANTIPADRÃO] `.collect()` sem amostragem prévia → estoura memória do driver
- [ANTIPADRÃO] `.count()` repetido sem `.cache()` → recalcula toda a chain
- [PADRÃO] Validar schema explicitamente antes de qualquer transformação

## GitLab CI/CD

- [PADRÃO] Cache de UV em `.uv-cache/` com key baseada em `uv.lock` reduz tempo de pipeline em ~60%
- [PADRÃO] PostgreSQL como service no CI — usar `POSTGRES_*` variables padrão

## C# / Unity

- [PADRÃO] Evitar singletons estáticos → preferir referências diretas ou UnityEvents
- [ANTIPADRÃO] `FindObjectOfType` em runtime → substituir por injeção via Inspector
- [PADRÃO] ScriptableObjects para todas as configurações tunable

## Linux / Hyprland / Teclado

- [PADRÃO] Diagnosticar tecla quebrada no Wayland com `wev` — mostra keycode exato e keysym resolvido antes de tentar qualquer fix; nunca assumir keycode sem verificar
- [ANTIPADRÃO] Misturar `kb_file` com `kb_layout`/`kb_variant`/`kb_model`/`kb_rules` no Hyprland — o compositor reaplica o layout padrão por cima do `kb_file` após reloads, causando comportamento imprevisível
- [PADRÃO] Ao usar `kb_file`, remover todas as outras diretivas de teclado do `hyprland.conf`; o arquivo XKB já faz o include do layout base internamente
- [ANTIPADRÃO] Tentar produzir símbolos via `modifier_map None { <RCTL> }` no XKB — Hyprland intercepta teclas modificadoras (RCTL, LCTL, LALT…) no nível do compositor antes do XKB, então o modifier_map não resolve
- [PADRÃO] Para usar tecla modificadora física como tecla de símbolo no Hyprland: usar keyd para converter para um keycode neutro não-modificador (ex: `rightcontrol = 102nd` → `<LSGT>`), depois mapear o keycode neutro no XKB (`key <LSGT> { [slash, question, ...] }`)
- [PADRÃO] ThinkPad T14 Gen 2i ABNT2: solução final documentada em `~/claude-md/INSTALL.md` seção 9

## Instalação / Provisionamento

- [PADRÃO] Instalador que mexe em diretórios com secrets deve sempre: (1) snapshot timestamped antes; (2) preservar destinos sensíveis durante a cópia; (3) restore safety-net no fim. Implementado em `install.sh`/`install.ps1` via `backup_secrets`/`restore_secrets` → `~/.claude-md-backups/<ts>/`
- [PADRÃO] Arquivos que NUNCA devem ser sobrescritos pelo instalador: `.credentials.json`, `.claude.json`, `.model-cache.json`, `settings.local.json`, `.mcp.json` (pode ter senha de postgres real), `~/.secrets/claude-mprj.key`
- [ANTIPADRÃO] Pedir secret novo sem detectar se já existe — sempre mostrar `****<last4>` mascarado e perguntar se mantém antes de sobrescrever
- [PADRÃO] Reter apenas os N backups mais recentes (10) — evita explosão de espaço com chaves antigas em disco

## Observabilidade

- [PADRÃO] Chamar `configure_telemetry()` no `AppConfig.ready()` — garante instrumentação antes das requisições
- [ANTIPADRÃO] Colocar PII em atributos de span — viola LGPD e políticas Dynatrace
