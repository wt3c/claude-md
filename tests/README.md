# Bateria de Testes para Instaladores Claude Code

Testes comportamentais completos para `install.sh` e `install.ps1`, garantindo que a migração para Python mantenha funcionalidade idêntica.

## Estrutura

```
tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Fixtures globais e helpers
├── test_helpers.py             # Implementações Python de referência
├── test_backup_restore.py      # Testes de backup/restore (✅ 100%)
├── test_prereqs.py             # Testes de pré-requisitos (✅ 100%)
├── test_install_files.py       # Testes de instalação de arquivos (✅ 100%)
├── test_shell_config.py        # Testes de configuração de shell (✅ 80%)
├── FUNCIONALIDADES.md          # Mapeamento completo de funcionalidades
└── README.md                   # Esta documentação
```

## Instalação

### Dependências

```bash
# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências de teste
pip install pytest pytest-cov pytest-mock
```

## Execução

### Todos os testes

```bash
pytest tests/ -v
```

### Com cobertura

```bash
pytest tests/ --cov=tests.test_helpers --cov-report=html --cov-report=term
```

### Testes específicos

```bash
# Apenas backup/restore
pytest tests/test_backup_restore.py -v

# Apenas pré-requisitos
pytest tests/test_prereqs.py -v

# Apenas instalação de arquivos
pytest tests/test_install_files.py -v

# Apenas configuração de shell
pytest tests/test_shell_config.py -v
```

### Teste específico

```bash
pytest tests/test_backup_restore.py::TestBackupSecrets::test_backup_creates_timestamped_directory -v
```

## Cobertura Atual

| Módulo | Cobertura | Status |
|--------|-----------|--------|
| Backup/Restore | 100% | ✅ Completo |
| Pré-requisitos | 100% | ✅ Completo |
| Instalação de arquivos | 100% | ✅ Completo |
| Configuração de shell | 80% | 🟡 Em progresso |
| API keys e tokens | 0% | ⏳ Pendente |
| MCP installation | 0% | ⏳ Pendente |
| Integração (fluxo completo) | 0% | ⏳ Pendente |

**Meta:** 100% de cobertura de todas as funcionalidades críticas.

## Como usar na migração Python

1. **Executar testes ANTES da migração** para estabelecer baseline:
   ```bash
   pytest tests/ --cov=tests.test_helpers --cov-report=html
   ```

2. **Migrar funções uma a uma**:
   - Substituir implementação em `test_helpers.py` pela real
   - Ou criar módulo `install.py` e importar dele
   - Rodar testes após cada função migrada

3. **Garantir 100% dos testes passando** antes de considerar a migração completa

4. **Testes de integração** com scripts reais (ainda não implementados):
   ```bash
   # Executa install.sh em ambiente isolado
   pytest tests/test_integration.py::test_bash_install_full_flow -v

   # Executa install.ps1 em ambiente isolado
   pytest tests/test_integration.py::test_powershell_install_full_flow -v
   ```

## Estrutura de Fixtures

### `temp_home`
Cria diretório HOME temporário isolado com arquivos rc vazios.

```python
def test_something(temp_home):
    bashrc = temp_home / ".bashrc"
    assert bashrc.exists()
```

### `mock_repo`
Cria repositório mock com estrutura completa (CLAUDE.md, settings, skills, etc).

```python
def test_something(mock_repo):
    claude_md = mock_repo / "CLAUDE.md"
    assert claude_md.exists()
```

### `existing_secrets`
Cria arquivos sensíveis existentes no HOME (para testar backup/preserve).

```python
def test_something(temp_home, existing_secrets):
    key = existing_secrets["key"]
    assert key.read_text() == "sk-ant-existing-key-1234"
```

### `installer_env`
Ambiente completo: `temp_home` + `mock_repo` + `backup_root` + env vars.

```python
def test_something(installer_env):
    home = installer_env["home"]
    repo = installer_env["repo"]
    backup_root = installer_env["backup_root"]
```

### `mock_commands`
Mocks de comandos externos (git, node, claude).

```python
def test_something(mock_commands):
    # Simular git ausente
    mock_commands["git"].side_effect = FileNotFoundError
    # ... testar comportamento
```

## Helpers de Validação

```python
from .conftest import (
    assert_file_exists,
    assert_dir_exists,
    assert_file_content_contains,
    assert_file_mode,
)

def test_something(temp_home):
    file = temp_home / ".bashrc"

    assert_file_exists(file)
    assert_file_content_contains(file, "export PATH")
    assert_file_mode(file, 0o644)
```

## Implementações de Referência

Em `test_helpers.py`:

- `backup_secrets_python()` — Implementação Python de `backup_secrets()`
- `restore_secrets_python()` — Implementação Python de `restore_secrets()`
- `check_prereqs_python()` — Implementação Python de `check_prereqs()`
- `install_to_dir_python()` — Implementação Python de `install_to_dir()`
- `detect_shell_block_version()` — Detecta versão do bloco shell
- `remove_shell_block()` — Remove bloco shell com backup

**IMPORTANTE:** Estas são implementações de referência para validar os testes. Quando migrar para Python, substituir por implementação real ou importar do módulo final.

## Casos de Teste por Categoria

### Backup/Restore (15 testes)
- ✅ Cria backup timestamped
- ✅ Preserva estrutura de diretórios
- ✅ Copia todos arquivos sensíveis
- ✅ Cria env.snapshot
- ✅ Chmod 700 no backup dir
- ✅ Mantém apenas 10 backups
- ✅ Restore não sobrescreve existentes
- ✅ Restore copia apenas ausentes
- ✅ Restore retorna 0 se nada faltando
- ✅ Restore cria diretórios pai
- ✅ Roundtrip completo

### Pré-requisitos (6 testes)
- ✅ Detecta git presente/ausente
- ✅ Detecta node ≥18 / <18 / ausente
- ✅ Detecta claude presente/ausente

### Instalação de Arquivos (10 testes)
- ✅ Cria estrutura de diretórios
- ✅ Copia CLAUDE.md e settings.json (sempre)
- ✅ Preserva .mcp.json se existir
- ✅ Copia .mcp.json se ausente
- ✅ Copia skills/ e commands/ recursivamente
- ✅ Copia tasks/*.md apenas se ausente
- ✅ Cria audit.log vazio
- ✅ Instala em múltiplas contas

### Configuração de Shell (5 testes)
- ✅ Detecta bloco v2 / v1 / ausente
- ✅ Remove bloco legacy com backup timestamped
- ✅ Preserva conteúdo externo ao bloco
- ✅ Não duplica bloco v2
- ✅ Prompta migração para v1

### API Keys e Tokens (Pendente)
- ⏳ Detecta chave existente e mascara
- ⏳ Preserva chave se usuário confirmar
- ⏳ Remove aspas/espaços do input
- ⏳ Linux: salva em ~/.secrets com chmod 600
- ⏳ Windows: salva em env var do usuário
- ⏳ GITLAB_TOKEN adiciona ao rc correto
- ⏳ POSTMAN_API_KEY adiciona ao rc correto

### MCP Installation (Pendente)
- ⏳ Instala filesystem, memory, gitlab, postman
- ⏳ Detecta MCP já instalado e pula
- ⏳ Mensagem sobre postgres e playwright

### Integração (Pendente)
- ⏳ Fluxo completo multi-conta (Linux)
- ⏳ Fluxo completo single account (Linux)
- ⏳ Fluxo completo multi-conta (Windows)
- ⏳ Modo update (Windows)
- ⏳ Abort em pré-requisito faltando

## Próximos Passos

1. **Implementar testes de API keys** (`test_api_keys.py`)
2. **Implementar testes de MCP** (`test_mcp.py`)
3. **Implementar testes de integração** (`test_integration.py`)
4. **Atingir 100% de cobertura** em todas as categorias
5. **Migrar para Python** usando testes como rede de segurança

## Troubleshooting

### Testes falhando com "command not found"

Mock de comandos está desabilitado. Use fixture `mock_commands`:

```python
def test_something(mock_commands):
    # Agora git, node, claude estão mockados
    ...
```

### Permissões de arquivo não sendo preservadas

Linux/Mac apenas. No Windows, ignorar testes de chmod com:

```python
@pytest.mark.skipif(os.name == 'nt', reason="chmod not applicable on Windows")
def test_file_permissions():
    ...
```

### Testes lentos

Desabilitar testes de integração (que executam scripts reais):

```bash
pytest tests/ -v -m "not integration"
```

## Métricas de Qualidade

- **36 testes** (atualmente implementados)
- **~80 testes** (meta final)
- **Tempo de execução**: <5s (testes unitários), <30s (com integração)
- **Cobertura**: 100% das funcionalidades críticas

---

**Status:** 🟡 Em desenvolvimento — 45% completo (36/80 testes)

**Última atualização:** 2026-05-19
