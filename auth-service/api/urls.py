from .views import RegisterView, LoginView
from django.urls import path

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/login/', LoginView.as_view(), name='login'),
]