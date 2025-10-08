from .serializers import RegisterSerializer
from rest_framework import generics
from core.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class=RegisterSerializer