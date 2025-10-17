import factory
from factory.django import DjangoModelFactory
from faker import Faker
from core.models import User

fake = Faker('pt_BR')

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)
        skip_postgeneration_save = True

    email = factory.LazyAttribute(lambda _: fake.email())
    role = 'client'
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if create:
            password = extracted if extracted else 'testpass123'
            obj.set_password(password)
            obj.save()

class AdminUserFactory(UserFactory):
    role = 'admin'
    is_staff = True
    is_superuser = True

class CollaboratorUserFactory(UserFactory):
    role = 'collaborator'

class ClientUserFactory(UserFactory):
    role = 'client'