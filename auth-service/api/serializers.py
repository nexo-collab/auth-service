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
        self._validate_password(attrs)
        self._validate_admin(attrs)
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

    def _validate_password(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs
    
    def _validate_admin(self, attrs):
        if attrs.get('is_staff') or attrs.get('role') == 'admin':
            if User.objects.filter(role='admin').exists():
                raise serializers.ValidationError({"role": "Só pode existir um único admin no sistema"})
        return attrs

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not all([email, password]):
            raise serializers.ValidationError("Email e senha são obrigatórios.")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Usuário não encontrado.")

        if not user.check_password(password):
            raise serializers.ValidationError("Senha inválida.")

        attrs['user'] = user
        return attrs