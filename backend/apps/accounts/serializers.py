"""
Serializers pour l'app accounts.

- RegisterSerializer  : inscription d'un nouveau client
- LoginSerializer     : validation des identifiants
- UserSerializer      : lecture/modification du profil
- UserAdminSerializer : lecture étendue pour l'admin
"""
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Sérialisation pour l'inscription.
    Le mot de passe est haché avant la sauvegarde.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Minimum 8 caractères',
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Répétez le mot de passe',
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'password', 'password_confirm',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Les mots de passe ne correspondent pas.'}
            )
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        # Le rôle est toujours 'client' à l'inscription publique
        user = User(role=User.Role.CLIENT, **validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Validation des identifiants de connexion."""
    username = serializers.CharField(help_text='Nom d\'utilisateur ou email')
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Tentative de connexion par username
        user = authenticate(username=username, password=password)

        # Tentative par email si username échoue
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError(
                'Identifiants invalides. Vérifiez votre nom d\'utilisateur et mot de passe.'
            )
        if not user.is_active:
            raise serializers.ValidationError('Ce compte est désactivé.')

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Profil utilisateur — lecture et modification."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'address', 'role', 'avatar',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['role', 'date_joined', 'is_active']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Profil complet pour l'administrateur.
    Permet de modifier le rôle d'un utilisateur.
    """
    full_name = serializers.SerializerMethodField()
    reservations_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'address', 'role', 'avatar',
            'is_active', 'date_joined', 'reservations_count',
        ]
        read_only_fields = ['date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_reservations_count(self, obj):
        return obj.reservations.count()


class ChangePasswordSerializer(serializers.Serializer):
    """Changement de mot de passe."""
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Les mots de passe ne correspondent pas.'}
            )
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mot de passe actuel incorrect.')
        return value
