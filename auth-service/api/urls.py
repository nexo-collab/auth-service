from .views import RegisterView, LoginView, UserListAPIView, UserRetriveAPIView
from django.urls import path

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/user/', UserListAPIView.as_view(), name='users'),
    path('auth/user/<uuid:pk>/', UserRetriveAPIView.as_view(), name='user'),
]