import pytest
from api.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from core.models import User
from core.factories import UserFactory, AdminUserFactory


@pytest.mark.django_db
class TestUserSerializer:
    """Testes para UserSerializer"""

    def test_user_serializer_contains_expected_fields(self):
        """Testa que o serializer contém os campos esperados"""
        user = UserFactory()
        serializer = UserSerializer(user)
        assert set(serializer.data.keys()) == {'user_id', 'email', 'role'}

    def test_user_serializer_does_not_expose_password(self):
        """Testa que o serializer não expõe a senha"""
        user = UserFactory()
        serializer = UserSerializer(user)
        assert 'password' not in serializer.data


@pytest.mark.django_db
class TestRegisterSerializer:
    """Testes para RegisterSerializer"""

    def test_valid_registration_data(self):
        """Testa registro com dados válidos"""
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'client'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'newuser@example.com'
        assert user.role == 'client'
        assert user.check_password('SecurePass123!')

    def test_passwords_must_match(self):
        """Testa que as senhas devem coincidir"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass123!',
            'role': 'client'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        assert 'As senhas não coincidem.' in str(serializer.errors['password'])

    def test_email_must_be_unique(self):
        """Testa que email deve ser único"""
        UserFactory(email='existing@example.com')
        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'client'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_weak_password_is_rejected(self):
        """Testa que senha fraca é rejeitada"""
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password2': '123',
            'role': 'client'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_email_is_required(self):
        """Testa que email é obrigatório"""
        data = {
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'client'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_role_is_required(self):
        """Testa que role é obrigatório"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'role' in serializer.errors

    def test_cannot_create_multiple_admins(self):
        """Testa que não pode criar múltiplos admins"""
        AdminUserFactory()  # Cria primeiro admin
        data = {
            'email': 'secondadmin@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'admin'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'role' in serializer.errors
        assert 'Só pode existir um único admin no sistema' in str(serializer.errors['role'])

    def test_can_create_admin_when_none_exists(self):
        """Testa que pode criar admin quando nenhum existe"""
        data = {
            'email': 'admin@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'admin'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.role == 'admin'

    def test_password2_is_not_saved(self):
        """Testa que password2 não é salvo no banco"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'client'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert not hasattr(user, 'password2')


@pytest.mark.django_db
class TestLoginSerializer:
    """Testes para LoginSerializer"""

    def test_valid_login_credentials(self):
        """Testa login com credenciais válidas"""
        user = UserFactory(email='user@example.com', password='testpass123')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user

    def test_invalid_email(self):
        """Testa login com email inválido"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'Credenciais inválidas.' in str(serializer.errors)

    def test_invalid_password(self):
        """Testa login com senha inválida"""
        UserFactory(email='user@example.com', password='correctpass')
        data = {
            'email': 'user@example.com',
            'password': 'wrongpass'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'Credenciais inválidas.' in str(serializer.errors)

    def test_email_is_required(self):
        """Testa que email é obrigatório"""
        data = {'password': 'testpass123'}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_password_is_required(self):
        """Testa que senha é obrigatória"""
        data = {'email': 'user@example.com'}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_password_is_write_only(self):
        """Testa que senha é write-only"""
        user = UserFactory(email='user@example.com', password='testpass123')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        serializer.is_valid()
        # A senha não deve aparecer nos dados validados de forma exposta
        assert 'password' not in str(serializer.validated_data.get('user', {}))