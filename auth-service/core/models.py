import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from .managers import UserManager

# Tipos de usuários disponíveis
TYPES_USER_CHOICES = [
    ("client", _("Client")),
    ("collaborator", _("Collaborator")),
    ("admin", _("Admin")),
]

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        max_length=12, choices=TYPES_USER_CHOICES, default="client"
    )
    
    class Meta:
        db_table = "User"
        ordering = ["role"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.user_id} - {self.email}"
