"""
Modèle utilisateur personnalisé avec rôles.

Rôles disponibles:
- client      : peut réserver, payer, gérer ses réservations
- receptionist: peut confirmer, faire le check-in/check-out
- admin       : accès total (chambres, tarifs, utilisateurs)
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur personnalisé avec gestion des rôles.
    Étend AbstractUser pour conserver username, password, first_name, last_name, email.
    """

    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        RECEPTIONIST = 'receptionist', 'Réceptionniste'
        ADMIN = 'admin', 'Administrateur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name='Rôle',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Téléphone',
    )
    address = models.TextField(
        blank=True,
        verbose_name='Adresse',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar',
    )

    # Champs hérités d'AbstractUser utilisés :
    # username, password, email, first_name, last_name, is_active, date_joined

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ---- Helpers de rôle ----

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_staff_member(self):
        """Réceptionniste OU administrateur."""
        return self.role in [self.Role.RECEPTIONIST, self.Role.ADMIN]
