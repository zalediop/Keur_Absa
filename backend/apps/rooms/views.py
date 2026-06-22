"""
Vues pour l'app rooms.

Endpoints:
  GET    /api/rooms/                 → Liste chambres disponibles (public, filtres)
  POST   /api/rooms/                 → Créer chambre (admin)
  GET    /api/rooms/{id}/            → Détail chambre (public)
  PUT    /api/rooms/{id}/            → Modifier chambre (admin)
  DELETE /api/rooms/{id}/            → Supprimer chambre (admin)
  GET    /api/rooms/categories/      → Liste catégories (public)
  POST   /api/rooms/categories/      → Créer catégorie (admin)
  GET    /api/rooms/categories/{id}/ → Détail catégorie (public)
  GET    /api/rooms/rates/           → Tarifs saisonniers (auth)
  POST   /api/rooms/rates/           → Créer tarif (admin)
"""
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import RoomCategory, Room, SeasonalRate
from .serializers import (
    RoomCategorySerializer,
    RoomSerializer,
    RoomAvailabilitySerializer,
    SeasonalRateSerializer,
)
from apps.accounts.permissions import IsAdminRole, IsReceptionistOrAdmin


@extend_schema(tags=['rooms'])
class RoomCategoryViewSet(viewsets.ModelViewSet):
    """
    Gestion des catégories de chambres.

    - Lecture : public
    - Création/modification/suppression : admin uniquement
    """
    queryset = RoomCategory.objects.filter(is_active=True)
    serializer_class = RoomCategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminRole()]


@extend_schema(tags=['rooms'])
class RoomViewSet(viewsets.ModelViewSet):
    """
    Gestion des chambres.

    **Filtres disponibles (GET /api/rooms/)** :
    - `check_in=YYYY-MM-DD` : date d'arrivée
    - `check_out=YYYY-MM-DD` : date de départ
    - `category=<id>` : filtrer par catégorie
    - `min_price=<montant>` : prix minimum par nuit
    - `max_price=<montant>` : prix maximum par nuit
    - `capacity=<nb>` : capacité minimum

    Si `check_in` et `check_out` sont fournis, seules les chambres **disponibles**
    sur cette période sont retournées (pas de réservation active qui chevauche).
    """
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminRole()]

    def get_serializer_class(self):
        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')
        if check_in and check_out and self.action == 'list':
            return RoomAvailabilitySerializer
        return RoomSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['check_in'] = self.request.query_params.get('check_in')
        context['check_out'] = self.request.query_params.get('check_out')
        return context

    def get_queryset(self):
        queryset = Room.objects.select_related('category').filter(is_active=True)

        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')
        category = self.request.query_params.get('category')
        capacity = self.request.query_params.get('capacity')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        # ---- Filtre de disponibilité ----
        if check_in and check_out:
            try:
                ci = datetime.strptime(check_in, '%Y-%m-%d').date()
                co = datetime.strptime(check_out, '%Y-%m-%d').date()

                if ci >= co:
                    return Room.objects.none()

                # Récupérer les IDs des chambres avec une réservation active qui chevauche
                from apps.reservations.models import Reservation
                booked_room_ids = Reservation.objects.filter(
                    status__in=['pending', 'confirmed', 'checked_in'],
                    check_in_date__lt=co,
                    check_out_date__gt=ci,
                ).values_list('room_id', flat=True)

                queryset = queryset.exclude(id__in=booked_room_ids)
                # Exclure aussi les chambres en maintenance
                queryset = queryset.exclude(status='maintenance')

            except ValueError:
                pass  # Dates invalides — ignorer le filtre

        # ---- Autres filtres ----
        if category:
            queryset = queryset.filter(category_id=category)

        if capacity:
            try:
                queryset = queryset.filter(category__max_occupancy__gte=int(capacity))
            except ValueError:
                pass

        if min_price:
            try:
                queryset = queryset.filter(category__base_price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(category__base_price__lte=float(max_price))
            except ValueError:
                pass

        return queryset.order_by('floor', 'number')

    @extend_schema(
        summary="Liste des chambres disponibles avec filtre par dates",
        parameters=[
            OpenApiParameter('check_in', str, description='Date arrivée (YYYY-MM-DD)'),
            OpenApiParameter('check_out', str, description='Date départ (YYYY-MM-DD)'),
            OpenApiParameter('category', int, description='ID de la catégorie'),
            OpenApiParameter('capacity', int, description='Capacité minimum'),
            OpenApiParameter('min_price', float, description='Prix min par nuit'),
            OpenApiParameter('max_price', float, description='Prix max par nuit'),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['rates'])
class SeasonalRateViewSet(viewsets.ModelViewSet):
    """
    Gestion des tarifs saisonniers.

    - Lecture : personnel authentifié
    - Création/modification/suppression : admin uniquement
    """
    queryset = SeasonalRate.objects.select_related('category').all()
    serializer_class = SeasonalRateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsReceptionistOrAdmin()]
        return [IsAuthenticated(), IsAdminRole()]
