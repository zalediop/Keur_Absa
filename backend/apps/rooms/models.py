"""
Modèles pour la gestion des chambres.

Tables:
- RoomCategory   : Catégories (Standard, Deluxe, Suite, etc.)
- Room           : Chambres individuelles
- SeasonalRate   : Tarifs saisonniers par catégorie et période
"""
from django.db import models
from django.core.validators import MinValueValidator


class RoomCategory(models.Model):
    """
    Catégorie de chambre (ex: Standard, Deluxe, Suite Présidentielle).
    Définit le prix de base et les commodités communes à toutes les chambres de cette catégorie.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la catégorie',
    )
    description = models.TextField(
        verbose_name='Description',
    )
    max_occupancy = models.PositiveIntegerField(
        default=2,
        verbose_name='Capacité maximale (personnes)',
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix de base par nuit (FCFA)',
    )
    amenities = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Commodités',
        help_text='Ex: ["WiFi", "Climatisation", "TV", "Minibar"]',
    )
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name='Image',
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie de chambre'
        verbose_name_plural = 'Catégories de chambres'
        ordering = ['base_price']

    def __str__(self):
        return f"{self.name} — {self.base_price} FCFA/nuit"


class Room(models.Model):
    """
    Chambre individuelle.
    Une chambre appartient à une catégorie et a un statut (disponible/occupée/maintenance).
    """

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponible'
        OCCUPIED = 'occupied', 'Occupée'
        MAINTENANCE = 'maintenance', 'En maintenance'
        CLEANING = 'cleaning', 'En nettoyage'

    number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Numéro de chambre',
        help_text='Ex: 101, A2, PH1',
    )
    floor = models.PositiveIntegerField(
        verbose_name='Étage',
    )
    category = models.ForeignKey(
        RoomCategory,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='Catégorie',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        verbose_name='Statut',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description spécifique',
        help_text='Informations spécifiques à cette chambre (vue mer, coin salon...)',
    )
    image = models.ImageField(
        upload_to='rooms/',
        null=True,
        blank=True,
        verbose_name='Photo principale',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active (visible aux clients)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chambre'
        verbose_name_plural = 'Chambres'
        ordering = ['floor', 'number']

    def __str__(self):
        return f"Chambre {self.number} — {self.category.name} (Étage {self.floor})"

    def get_current_price(self, date=None):
        """
        Retourne le tarif applicable à une date donnée.
        Si aucun tarif saisonnier ne correspond, retourne le prix de base.
        """
        from datetime import date as date_type
        if date is None:
            date = date_type.today()

        seasonal = self.category.seasonal_rates.filter(
            start_date__lte=date,
            end_date__gte=date,
        ).first()

        if seasonal:
            return seasonal.price_per_night
        return self.category.base_price


class SeasonalRate(models.Model):
    """
    Tarif saisonnier pour une catégorie de chambre sur une période donnée.
    Exemple : Haute saison (Noël), prix 3× supérieur au tarif de base.

    Règle métier : les périodes ne doivent pas se chevaucher pour une même catégorie.
    """
    category = models.ForeignKey(
        RoomCategory,
        on_delete=models.CASCADE,
        related_name='seasonal_rates',
        verbose_name='Catégorie',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nom de la saison',
        help_text='Ex: Haute saison, Noël & Nouvel An, Été',
    )
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix par nuit (FCFA)',
    )

    class Meta:
        verbose_name = 'Tarif saisonnier'
        verbose_name_plural = 'Tarifs saisonniers'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} | {self.category.name} | {self.start_date} → {self.end_date}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('La date de début doit être antérieure à la date de fin.')
