from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from core.models import User

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este e-mail já está em uso.")]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirme a senha")

    class Meta:
        model = User
        fields = ('email', 'role', 'password', 'password2') 
        extra_kwargs = {
            'role': {'required': True}
        }

    def validate(self, attrs):
        """
        Validação customizada para garantir que as senhas coincidem.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        """
        Cria e retorna um novo usuário após a validação.
        """
        validated_data.pop('password2', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para exibir os dados de um usuário.
    Apenas para leitura (serialização).
    """
    class Meta:
        model = User
        fields = ('user_id', 'email', 'role', 'is_active', 'is_staff')
        read_only_fields = fields