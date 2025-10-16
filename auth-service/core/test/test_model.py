import pytest
from django.db import IntegrityError
from core.models import User
from core.factories import UserFactory, AdminUserFactory, CollaboratorUserFactory


@pytest.mark.django_db
class TestUserModel:
    """Testes para o modelo User"""

    def test_create_user_with_email(self):
        """Testa criação de usuário com email"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='client'
        )
        assert user.email == 'test@example.com'
        assert user.role == 'client'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.check_password('testpass123')

    def test_create_user_without_email_raises_error(self):
        """Testa que criar usuário sem email levanta erro"""
        with pytest.raises(ValueError, match="O Email é necessário para criar um usuário."):
            User.objects.create_user(email='', password='testpass123')

    def test_create_superuser(self):
        """Testa criação de superusuário"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.is_superuser is True
        assert admin.is_staff is True
        assert admin.is_active is True

    def test_email_must_be_unique(self):
        """Testa que email deve ser único"""
        UserFactory(email='duplicate@example.com')
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(email='duplicate@example.com', password='password123')

    def test_user_string_representation(self):
        """Testa representação string do usuário"""
        user = UserFactory(email='test@example.com')
        assert str(user) == f"{user.user_id} - test@example.com"

    def test_user_uuid_is_generated(self):
        """Testa que UUID é gerado automaticamente"""
        user = UserFactory()
        assert user.user_id is not None
        assert len(str(user.user_id)) == 36  # UUID format

    def test_user_role_choices(self):
        """Testa diferentes tipos de roles"""
        client = UserFactory(role='client')
        collaborator = CollaboratorUserFactory()
        admin = AdminUserFactory()

        assert client.role == 'client'
        assert collaborator.role == 'collaborator'
        assert admin.role == 'admin'

    def test_user_default_values(self):
        """Testa valores padrão do usuário"""
        user = User.objects.create_user(
            email='default@example.com',
            password='pass123'
        )
        assert user.role == 'client'
        assert user.is_active is True
        assert user.is_staff is False

    def test_password_is_hashed(self):
        """Testa que a senha é armazenada como hash"""
        user = UserFactory()
        assert user.password != 'testpass123'
        assert user.password.startswith('pbkdf2_sha256$')

    def test_user_permissions_mixin(self):
        """Testa que o usuário herda de PermissionsMixin"""
        user = UserFactory()
        assert hasattr(user, 'is_superuser')
        assert hasattr(user, 'groups')
        assert hasattr(user, 'user_permissions')