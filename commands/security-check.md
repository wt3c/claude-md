---
description: Auditoria de segurança focada em OWASP Top 10 para código Python/Django
---

Realize uma auditoria de segurança completa neste projeto Django, focando em OWASP Top 10.

## Itens a verificar

### A01 — Controle de Acesso Quebrado
- Views sem decorators de autenticação (@login_required, @permission_required)
- Endpoints da API sem permissões DRF adequadas
- Acesso direto a objetos por ID sem verificar ownership
- IDOR — alguém pode acessar objeto de outro usuário?

### A02 — Falhas Criptográficas
- Passwords armazenadas sem hash ou com MD5/SHA1
- Dados sensíveis em texto claro no banco
- Comunicação HTTP em vez de HTTPS
- Secrets em código ou variáveis de ambiente não gerenciadas

### A03 — Injection
- Queries SQL com string formatting (usar ORM ou parâmetros)
- Shell injection em subprocess/os.system
- Template injection
- Path traversal em file operations

### A04 — Design Inseguro
- Ausência de rate limiting em endpoints críticos
- Falta de validação de input em boundaries
- Lógica de negócio exposta desnecessariamente na API

### A05 — Configuração Incorreta
- DEBUG=True em produção
- SECRET_KEY padrão ou fraca
- ALLOWED_HOSTS com wildcard em produção
- CORS permissivo demais
- Cabeçalhos de segurança ausentes

### A06 — Componentes Vulneráveis
- Dependências desatualizadas com CVEs conhecidos
- Verificar com: uv run pip audit

### A07 — Falhas de Identificação e Autenticação
- Sessões sem timeout
- Senhas fracas permitidas
- Ausência de 2FA em endpoints críticos

### A09 — Logging e Monitoramento Insuficientes
- Ações críticas sem log (login, alteração de dados sensíveis)
- Logs com dados pessoais (PII)
- Falhas sem alertas configurados

Retorne relatório em formato:
**[CRÍTICO | ALTO | MÉDIO | BAIXO]** arquivo:linha — descrição — recomendação
