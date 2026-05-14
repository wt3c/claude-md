---
name: django-service-layer
description: >
  Aplicar o padrão Service/Repository com Protocol-based DI
  em código Django/DRF. Usar quando criar ou refatorar views,
  serializers ou models que contêm lógica de negócio.
---

# Django Service Layer Pattern

## Quando aplicar

Esta skill deve ser usada quando:
- View contém lógica de negócio (mais que apenas orquestração HTTP)
- Model tem métodos além de `save()`, `clean()`, `__str__()`
- Lógica duplicada entre views, tasks Celery ou scripts
- Precisa testar lógica de negócio sem mocks de HTTP
- Precisa reutilizar lógica em diferentes contextos (API, CLI, tasks)

## Estrutura alvo

```
apps/
  minha_app/
    models.py          # apenas dados e validação simples
    repositories.py    # acesso a dados (Protocol-based)
    services.py        # lógica de negócio
    views.py           # apenas orquestração HTTP
    serializers.py     # validação de input/output
    tests/
      test_services.py      # testes de lógica (sem HTTP)
      test_repositories.py  # testes de acesso a dados
      test_views.py         # testes de integração HTTP
```

## Protocolo base (Repository)

```python
# apps/minha_app/repositories.py
from typing import Protocol, Optional
from .models import User

class UserRepository(Protocol):
    """Interface para acesso a dados de usuários."""
    
    def get_by_id(self, user_id: int) -> User:
        """Busca usuário por ID. Levanta User.DoesNotExist se não encontrar."""
        ...
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email. Retorna None se não encontrar."""
        ...
    
    def save(self, user: User) -> User:
        """Persiste usuário no banco."""
        ...
    
    def list_active(self) -> list[User]:
        """Lista todos usuários ativos."""
        ...

class DjangoUserRepository:
    """Implementação Django ORM do UserRepository."""
    
    def get_by_id(self, user_id: int) -> User:
        return User.objects.select_related('profile').get(id=user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    def save(self, user: User) -> User:
        user.save()
        return user
    
    def list_active(self) -> list[User]:
        return list(User.objects.filter(is_active=True))
```

## Service Layer

```python
# apps/minha_app/services.py
from typing import Protocol
from django.core.mail import send_mail
from .models import User
from .repositories import UserRepository

class UserService:
    """Lógica de negócio de usuários."""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def activate_user(self, user_id: int) -> User:
        """
        Ativa um usuário e envia email de boas-vindas.
        
        Raises:
            User.DoesNotExist: se usuário não existe
        """
        user = self.repository.get_by_id(user_id)
        
        if user.is_active:
            return user  # já ativo, nada a fazer
        
        user.is_active = True
        user = self.repository.save(user)
        
        # Enviar email de boas-vindas
        send_mail(
            subject='Bem-vindo!',
            message=f'Olá {user.first_name}, sua conta foi ativada.',
            from_email='noreply@example.com',
            recipient_list=[user.email],
        )
        
        return user
    
    def register_user(self, email: str, password: str, first_name: str) -> User:
        """
        Registra novo usuário.
        
        Raises:
            ValueError: se email já existe
        """
        existing = self.repository.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} já está em uso")
        
        user = User(
            email=email,
            first_name=first_name,
            is_active=False  # ativação manual
        )
        user.set_password(password)
        
        return self.repository.save(user)
```

## Views (apenas orquestração)

```python
# apps/minha_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import UserService
from .repositories import DjangoUserRepository
from .serializers import UserSerializer

class UserActivateView(APIView):
    """Ativa um usuário existente."""
    
    def post(self, request, user_id):
        service = UserService(DjangoUserRepository())
        
        try:
            user = service.activate_user(user_id)
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserRegisterView(APIView):
    """Registra novo usuário."""
    
    def post(self, request):
        service = UserService(DjangoUserRepository())
        
        try:
            user = service.register_user(
                email=request.data['email'],
                password=request.data['password'],
                first_name=request.data['first_name']
            )
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except KeyError as e:
            return Response(
                {'error': f'Campo obrigatório: {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )
```

## Testes (sem HTTP)

```python
# apps/minha_app/tests/test_services.py
import pytest
from unittest.mock import Mock
from ..services import UserService
from ..models import User

class TestUserService:
    def test_activate_user_success(self):
        # Arrange
        user = User(id=1, email='test@example.com', is_active=False)
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = user
        mock_repo.save.return_value = user
        
        service = UserService(mock_repo)
        
        # Act
        result = service.activate_user(user_id=1)
        
        # Assert
        assert result.is_active is True
        mock_repo.get_by_id.assert_called_once_with(1)
        mock_repo.save.assert_called_once()
    
    def test_activate_user_already_active(self):
        # Arrange
        user = User(id=1, email='test@example.com', is_active=True)
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = user
        
        service = UserService(mock_repo)
        
        # Act
        result = service.activate_user(user_id=1)
        
        # Assert
        assert result.is_active is True
        mock_repo.save.assert_not_called()  # não salva se já ativo
    
    def test_register_user_email_already_exists(self):
        # Arrange
        existing_user = User(id=1, email='existing@example.com')
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = existing_user
        
        service = UserService(mock_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="já está em uso"):
            service.register_user(
                email='existing@example.com',
                password='pass123',
                first_name='Test'
            )
```

## Regras

1. **NUNCA** importar `request` dentro de services
2. Services recebem **dados puros**, não objetos HTTP (request, response)
3. Repository **sempre** recebe e retorna domain objects (models)
4. Repository **não** contém lógica de negócio (apenas acesso a dados)
5. Views são **finas** — apenas traduzem HTTP ↔ Service
6. Testes de services **não** precisam de banco (usar mocks de repository)
7. Usar **Protocol** em vez de classes abstratas (mais flexível)

## Benefícios

- Lógica de negócio 100% testável sem mocks de HTTP ou banco
- Reutilização em views, tasks Celery, scripts CLI, testes
- Separação clara de responsabilidades (SRP)
- Fácil substituir implementação (ex: trocar Django ORM por SQLAlchemy)
- Código mais limpo e fácil de manter

## Quando NÃO usar

- CRUDs simples sem lógica (usar apenas ModelViewSet do DRF)
- Views read-only triviais (lista, detalhe)
- Protótipos rápidos (pode adicionar depois)
