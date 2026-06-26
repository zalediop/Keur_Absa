"""
Vues pour l'app accounts.

Endpoints:
  POST   /api/auth/register/         → Inscription (public)
  POST   /api/auth/login/            → Login → JWT tokens (public)
  POST   /api/auth/token/refresh/    → Rafraîchir access token (public)
  POST   /api/auth/logout/           → Invalider refresh token (auth)
  GET    /api/auth/profile/          → Mon profil (auth)
  PATCH  /api/auth/profile/          → Modifier mon profil (auth)
  POST   /api/auth/change-password/  → Changer mot de passe (auth)
  GET    /api/auth/users/            → Liste utilisateurs (admin)
  GET    /api/auth/users/{id}/       → Détail utilisateur (admin)
  PATCH  /api/auth/users/{id}/       → Modifier rôle (admin)
"""
# pyrefly: ignore [missing-import]
from rest_framework import generics, status
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework.views import APIView
# pyrefly: ignore [missing-import]
from rest_framework.permissions import AllowAny, IsAuthenticated
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.tokens import RefreshToken
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.exceptions import TokenError
# pyrefly: ignore [missing-import]
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserAdminSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdminRole


# ============================================================
# ENDPOINTS PUBLICS
# ============================================================

@extend_schema(tags=['auth'])
class RegisterView(generics.CreateAPIView):
    """
    Inscription d'un nouveau client.

    Crée un compte avec le rôle 'client' par défaut.
    Retourne les informations du nouvel utilisateur.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Générer les tokens JWT pour connexion automatique après inscription
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'message': 'Inscription réussie ! Bienvenue sur HotelBookCI.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['auth'])
class LoginView(APIView):
    """
    Connexion utilisateur — retourne les tokens JWT.

    **Flux JWT** :
    1. Envoyez username + password
    2. Récupérez `access` et `refresh` dans la réponse
    3. Stockez-les dans `localStorage`
    4. Ajoutez `Authorization: Bearer <access>` à chaque requête protégée
    5. Quand le token expire (401), utilisez `/token/refresh/` avec le `refresh`
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                'message': f'Bienvenue, {user.get_full_name() or user.username} !',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(access),
                    'refresh': str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['auth'])
class LogoutView(APIView):
    """
    Déconnexion — invalide le refresh token (blacklist).

    Côté frontend, supprimez également les tokens du localStorage.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Le refresh token est requis.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Déconnexion réussie.'},
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {'error': 'Token invalide ou déjà révoqué.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ============================================================
# ENDPOINTS AUTHENTIFIÉS
# ============================================================

@extend_schema(tags=['auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Mon profil — lecture et modification.

    GET  : Retourne les informations du compte connecté.
    PATCH: Modifie les champs (first_name, last_name, phone, address, avatar).
    Le rôle ne peut pas être modifié ici (admin seulement).
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['auth'])
class ChangePasswordView(APIView):
    """
    Changer son mot de passe.

    Nécessite l'ancien mot de passe pour validation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(
            {'message': 'Mot de passe modifié avec succès.'},
            status=status.HTTP_200_OK,
        )


# ============================================================
# ENDPOINTS ADMIN
# ============================================================

@extend_schema(tags=['auth'])
class UserListView(generics.ListAPIView):
    """
    Liste de tous les utilisateurs — **Admin uniquement**.

    Filtres disponibles :
    - `?role=client` → filtrer par rôle
    - `?search=nom` → rechercher par nom/username/email
    """
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        return queryset.distinct()


@extend_schema(tags=['auth'])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détail, modification et suppression d'un utilisateur — **Admin uniquement**.

    PATCH permet de modifier le rôle d'un utilisateur.
    La suppression de son propre compte est interdite.
    """
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user:
            return Response(
                {'error': 'Impossible de supprimer votre propre compte administrateur.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
