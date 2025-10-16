import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import User
from core.factories import UserFactory, AdminUserFactory, CollaboratorUserFactory


@pytest.fixture
def api_client():
    """Fixture para cliente da API"""
    return APIClient()


@pytest.mark.django_db
class TestRegisterView:
    """Testes para RegisterView"""

    def test_register_user_successfully(self, api_client):
        """Testa registro bem-sucedido de usuário"""
        url = reverse('user-register')
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'client'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@example.com').exists()
        user = User.objects.get(email='newuser@example.com')
        assert user.role == 'client'

    def test_register_with_invalid_data(self, api_client):
        """Testa registro com dados inválidos"""
        url = reverse('user-register')
        data = {
            'email': 'invalidemail',
            'password': '123',
            'password2': '456',
            'role': 'client'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_with_duplicate_email(self, api_client):
        """Testa registro com email duplicado"""
        UserFactory(email='existing@example.com')
        url = reverse('user-register')
        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'client'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_admin_when_admin_exists(self, api_client):
        """Testa registro de admin quando já existe um"""
        AdminUserFactory()
        url = reverse('user-register')
        data = {
            'email': 'secondadmin@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'admin'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data

    def test_register_different_roles(self, api_client):
        """Testa registro de diferentes tipos de usuários"""
        url = reverse('user-register')
        
        roles = ['client', 'collaborator']
        for idx, role in enumerate(roles):
            data = {
                'email': f'{role}{idx}@example.com',
                'password': 'SecurePass123!',
                'password2': 'SecurePass123!',
                'role': role
            }
            response = api_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            user = User.objects.get(email=f'{role}{idx}@example.com')
            assert user.role == role


@pytest.mark.django_db
class TestLoginView:
    """Testes para LoginView"""

    def test_login_successfully(self, api_client):
        """Testa login bem-sucedido"""
        user = UserFactory(email='user@example.com', password='testpass123')
        url = reverse('login')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_with_invalid_email(self, api_client):
        """Testa login com email inválido"""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_login_with_invalid_password(self, api_client):
        """Testa login com senha inválida"""
        UserFactory(email='user@example.com', password='correctpass')
        url = reverse('login')
        data = {
            'email': 'user@example.com',
            'password': 'wrongpass'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_returns_valid_tokens(self, api_client):
        """Testa que o login retorna tokens válidos"""
        UserFactory(email='user@example.com', password='testpass123')
        url = reverse('login')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data['access'], str)
        assert isinstance(response.data['refresh'], str)
        assert len(response.data['access']) > 0
        assert len(response.data['refresh']) > 0


@pytest.mark.django_db
class TestUserListAPIView:
    """Testes para UserListAPIView"""

    def test_list_users(self, api_client):
        """Testa listagem de usuários"""
        UserFactory.create_batch(3)
        url = reverse('users')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_list_users_returns_correct_fields(self, api_client):
        """Testa que a listagem retorna campos corretos"""
        UserFactory(email='test@example.com', role='client')
        url = reverse('users')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        user_data = response.data[0]
        assert 'user_id' in user_data
        assert 'email' in user_data
        assert 'role' in user_data
        assert 'password' not in user_data

    def test_list_empty_users(self, api_client):
        """Testa listagem quando não há usuários"""
        url = reverse('users')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_users_different_roles(self, api_client):
        """Testa listagem de usuários com diferentes roles"""
        UserFactory(role='client')
        CollaboratorUserFactory()
        AdminUserFactory()
        
        url = reverse('users')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        roles = [user['role'] for user in response.data]
        assert 'client' in roles
        assert 'collaborator' in roles
        assert 'admin' in roles


@pytest.mark.django_db
class TestUserRetrieveAPIView:
    """Testes para UserRetrieveAPIView"""

    def test_retrieve_user_by_id(self, api_client):
        """Testa buscar usuário por ID"""
        user = UserFactory(email='test@example.com')
        url = reverse('user', kwargs={'pk': user.user_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['user_id'] == str(user.user_id)

    def test_retrieve_nonexistent_user(self, api_client):
        """Testa buscar usuário inexistente"""
        import uuid
        fake_uuid = uuid.uuid4()
        url = reverse('user', kwargs={'pk': fake_uuid})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_user_does_not_expose_password(self, api_client):
        """Testa que buscar usuário não expõe a senha"""
        user = UserFactory()
        url = reverse('user', kwargs={'pk': user.user_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'password' not in response.data

    def test_retrieve_user_contains_expected_fields(self, api_client):
        """Testa que usuário contém campos esperados"""
        user = UserFactory(email='test@example.com', role='collaborator')
        url = reverse('user', kwargs={'pk': user.user_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == {'user_id', 'email', 'role'}
        assert response.data['email'] == 'test@example.com'
        assert response.data['role'] == 'collaborator'