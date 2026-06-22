"""
Permissions personnalisées basées sur le rôle de l'utilisateur.

Usage dans les vues :
    permission_classes = [IsAuthenticated, IsAdminRole]
"""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Autorise uniquement les utilisateurs avec le rôle 'admin'."""

    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsReceptionistOrAdmin(BasePermission):
    """Autorise les réceptionnistes et les administrateurs."""

    message = "Accès réservé au personnel de l'hôtel."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['receptionist', 'admin']
        )


class IsClientOrAdmin(BasePermission):
    """Autorise les clients et les administrateurs."""

    message = "Accès réservé aux clients."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['client', 'admin']
        )


class IsOwnerOrStaff(BasePermission):
    """
    Autorise le propriétaire de l'objet OU le personnel (receptionist/admin).
    L'objet doit avoir un attribut 'client' ou 'user'.
    """

    message = "Vous n'avez pas la permission d'accéder à cette ressource."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        # Admin et réceptionniste peuvent tout voir
        if request.user.role in ['receptionist', 'admin']:
            return True
        # Le client ne peut accéder qu'à ses propres objets
        owner = getattr(obj, 'client', None) or getattr(obj, 'user', None)
        return owner == request.user
