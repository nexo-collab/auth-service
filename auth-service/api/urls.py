from .views import RegisterView
from django.urls import path

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
]