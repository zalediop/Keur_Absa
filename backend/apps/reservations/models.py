"""
Modèles pour la gestion des réservations, paiements et check-in/out.

Flux de statut d'une réservation:
  pending → confirmed → checked_in → checked_out
       ↘ cancelled (depuis pending ou confirmed)

Tables:
- Reservation : réservation client avec dates et statut
- Payment     : paiement lié à une réservation (OneToOne)
- CheckIn     : enregistrement check-in/check-out par le réceptionniste
"""
import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Reservation(models.Model):
    """
    Réservation d'une chambre par un client.

    Contraintes:
    - check_out > check_in
    - Pas de chevauchement de réservations sur la même chambre
    - Statut suit le flux: pending → confirmed → checked_in → checked_out / cancelled
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmée'
        CHECKED_IN = 'checked_in', 'Arrivé'
        CHECKED_OUT = 'checked_out', 'Parti'
        CANCELLED = 'cancelled', 'Annulée'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Client',
        limit_choices_to={'role': 'client'},
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Chambre',
    )
    check_in_date = models.DateField(verbose_name='Date d\'arrivée')
    check_out_date = models.DateField(verbose_name='Date de départ')
    adults = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Nombre d\'adultes',
    )
    children = models.PositiveIntegerField(
        default=0,
        verbose_name='Nombre d\'enfants',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Statut',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix total (FCFA)',
    )
    special_requests = models.TextField(
        blank=True,
        verbose_name='Demandes spéciales',
        help_text='Allergies, préférences, accessibilité...',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='reservation_checkout_after_checkin',
            ),
        ]

    def __str__(self):
        return (
            f"Réservation #{self.pk} — {self.client.get_full_name() or self.client.username} "
            f"| Chambre {self.room.number} "
            f"| {self.check_in_date} → {self.check_out_date}"
        )

    @property
    def nights(self):
        """Nombre de nuits."""
        return (self.check_out_date - self.check_in_date).days

    @property
    def is_cancellable(self):
        """Une réservation peut être annulée si elle est en attente ou confirmée."""
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED]

    def clean(self):
        super().clean()
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValidationError(
                    'La date de départ doit être postérieure à la date d\'arrivée.'
                )

    def calculate_total(self):
        """Calcule le prix total basé sur le tarif de la chambre et le nombre de nuits."""
        price_per_night = self.room.get_current_price(self.check_in_date)
        return price_per_night * self.nights


class Payment(models.Model):
    """
    Paiement associé à une réservation (relation OneToOne).

    Un seul paiement par réservation.
    Le statut du paiement suit: pending → completed / failed / refunded
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        COMPLETED = 'completed', 'Complété'
        FAILED = 'failed', 'Échoué'
        REFUNDED = 'refunded', 'Remboursé'

    class Method(models.TextChoices):
        CARD = 'card', 'Carte bancaire'
        CASH = 'cash', 'Espèces'
        TRANSFER = 'transfer', 'Virement bancaire'
        MOBILE = 'mobile', 'Mobile Money'

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='Réservation',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant (FCFA)',
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.CARD,
        verbose_name='Méthode de paiement',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Statut du paiement',
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='ID de transaction',
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de paiement',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement #{self.pk} — {self.amount} FCFA ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class CheckIn(models.Model):
    """
    Enregistrement du check-in et check-out physique par le réceptionniste.
    Lié à une réservation (OneToOne).
    """
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='checkin_record',
        verbose_name='Réservation',
    )
    receptionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_checkins',
        verbose_name='Réceptionniste',
    )
    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Heure d\'arrivée réelle',
    )
    checked_out_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Heure de départ réelle',
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Observations du réceptionniste lors du check-in/check-out',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Enregistrement Check-in/out'
        verbose_name_plural = 'Enregistrements Check-in/out'
        ordering = ['-created_at']

    def __str__(self):
        return f"CheckIn #{self.pk} — Réservation #{self.reservation_id}"
