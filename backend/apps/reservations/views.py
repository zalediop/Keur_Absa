"""
Vues pour l'app reservations.

Endpoints:
  POST   /api/reservations/                    → Créer réservation (client)
  GET    /api/reservations/                    → Lister réservations (filtré par rôle)
  GET    /api/reservations/{id}/               → Détail réservation
  PATCH  /api/reservations/{id}/cancel/        → Annuler réservation (client/admin)
  PATCH  /api/reservations/{id}/confirm/       → Confirmer réservation (réceptionniste/admin)
  POST   /api/reservations/{id}/checkin/       → Enregistrer check-in (réceptionniste/admin)
  POST   /api/reservations/{id}/checkout/      → Enregistrer check-out (réceptionniste/admin)
  GET    /api/payments/                        → Liste paiements (filtré par rôle)
  POST   /api/payments/                        → Créer paiement (client)
  GET    /api/payments/{id}/                   → Détail paiement
  GET    /api/stats/                           → Statistiques globales (staff/admin)
"""
# pyrefly: ignore [missing-import]
from django.utils import timezone
# pyrefly: ignore [missing-import]
from django.utils.timezone import now
# pyrefly: ignore [missing-import]
from django.db.models import Count, Sum, Q
# pyrefly: ignore [missing-import]
from rest_framework import viewsets, status
# pyrefly: ignore [missing-import]
from rest_framework.decorators import action, api_view, permission_classes
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import, parse-error]
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Reservation, Payment, CheckIn
from .serializers import (
    ReservationSerializer,
    ReservationCreateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    CheckInSerializer,
)
# pyrefly: ignore [missing-import]
from apps.accounts.permissions import IsAdminRole, IsReceptionistOrAdmin, IsOwnerOrStaff
# pyrefly: ignore [missing-import]
from apps.rooms.models import Room


@extend_schema(tags=['reservations'], summary='Statistiques globales du tableau de bord')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Retourne les statistiques globales pour les dashboards Admin et Réception.
    Utilise des agrégations SQL pour éviter de charger toutes les lignes en mémoire.
    """
    user = request.user
    today = timezone.localdate()

    # --- Statistiques réservations ---
    if user.role == 'client':
        res_qs = Reservation.objects.filter(client=user)
    else:
        res_qs = Reservation.objects.all()

    res_counts = res_qs.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        confirmed=Count('id', filter=Q(status='confirmed')),
        checked_in=Count('id', filter=Q(status='checked_in')),
        checked_out=Count('id', filter=Q(status='checked_out')),
        cancelled=Count('id', filter=Q(status='cancelled')),
        today_arrivals=Count('id', filter=Q(status='confirmed', check_in_date=today)),
    )

    # --- Revenus (réservations non annulées) ---
    revenue_data = res_qs.exclude(status='cancelled').aggregate(
        total_revenue=Sum('total_price')
    )
    total_revenue = revenue_data['total_revenue'] or 0

    # --- Statistiques chambres (admin/réception uniquement) ---
    room_stats = {}
    if user.role in ['admin', 'receptionist']:
        room_counts = Room.objects.filter(is_active=True).aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(status='available')),
            occupied=Count('id', filter=Q(status='occupied')),
            maintenance=Count('id', filter=Q(status='maintenance')),
            cleaning=Count('id', filter=Q(status='cleaning')),
        )
        room_stats = room_counts

    return Response({
        'reservations': res_counts,
        'revenue': str(total_revenue),
        'rooms': room_stats,
        'today': str(today),
    })



@extend_schema(tags=['reservations'])
class ReservationViewSet(viewsets.ModelViewSet):
    """
    Gestion des réservations.

    **Permissions par rôle** :
    - Client : voit uniquement ses propres réservations, peut créer et annuler
    - Réceptionniste : voit toutes les réservations, peut confirmer, check-in, check-out
    - Admin : accès total

    **Filtres** :
    - `?status=pending|confirmed|checked_in|checked_out|cancelled`
    - `?date_from=YYYY-MM-DD` : réservations à partir de cette date
    - `?date_to=YYYY-MM-DD` : réservations jusqu'à cette date
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Reservation.objects.select_related(
            'client', 'room', 'room__category',
        ).prefetch_related('payment', 'checkin_record')

        # Filtrage par rôle
        if user.role == 'client':
            queryset = queryset.filter(client=user)
        # receptionist et admin voient tout

        # Filtres optionnels
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        room_id = self.request.query_params.get('room')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(check_in_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(check_out_date__lte=date_to)
        if room_id:
            queryset = queryset.filter(room_id=room_id)

        # Filtre par date exacte d'arrivée (pour les arrivées du jour)
        check_in_date = self.request.query_params.get('check_in_date')
        if check_in_date:
            queryset = queryset.filter(check_in_date=check_in_date)

        return queryset.order_by('-created_at')

    def get_permissions(self):
        if self.action in ['confirm', 'perform_checkin', 'perform_checkout']:
            return [IsAuthenticated(), IsReceptionistOrAdmin()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Créer une nouvelle réservation — Client uniquement."""
        if request.user.role not in ['client', 'admin']:
            return Response(
                {'error': 'Seuls les clients peuvent créer des réservations.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Utiliser le serializer de création pour la validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        # Retourner la réservation complète (avec total_price, nights, etc.)
        output_serializer = ReservationSerializer(
            reservation,
            context=self.get_serializer_context(),
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Modification complète interdite — utiliser les actions spécifiques."""
        return Response(
            {'error': 'Utilisez les endpoints /cancel/, /confirm/, /checkin/, /checkout/'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(
        summary="Annuler une réservation",
        description="Annule une réservation en statut 'pending' ou 'confirmed'. "
                    "Le client ne peut annuler que ses propres réservations.",
        responses={200: ReservationSerializer, 400: OpenApiResponse(description='Erreur métier')},
    )
    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Annuler une réservation — Client (sa propre) ou Admin."""
        reservation = self.get_object()

        # Vérification propriété pour les clients
        if request.user.role == 'client' and reservation.client != request.user:
            return Response(
                {'error': 'Vous ne pouvez annuler que vos propres réservations.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not reservation.is_cancellable:
            return Response(
                {
                    'error': (
                        f'Impossible d\'annuler une réservation avec le statut '
                        f'"{reservation.get_status_display()}".'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        return Response(
            {
                'message': 'Réservation annulée avec succès.',
                'reservation': ReservationSerializer(reservation, context={'request': request}).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Confirmer une réservation",
        description="Confirme une réservation en statut 'pending'. "
                    "Réservé au réceptionniste et à l'administrateur.",
        responses={200: ReservationSerializer, 400: OpenApiResponse(description='Erreur métier')},
    )
    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm(self, request, pk=None):
        """Confirmer une réservation — Réceptionniste/Admin."""
        reservation = self.get_object()

        if reservation.status != Reservation.Status.PENDING:
            return Response(
                {
                    'error': (
                        f'Seules les réservations en attente peuvent être confirmées. '
                        f'Statut actuel: "{reservation.get_status_display()}".'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = Reservation.Status.CONFIRMED
        reservation.save()
        return Response(
            {
                'message': 'Réservation confirmée avec succès.',
                'reservation': ReservationSerializer(reservation, context={'request': request}).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Enregistrer le check-in",
        description="Enregistre l'arrivée physique du client. "
                    "La réservation doit être confirmée. Crée un enregistrement CheckIn. "
                    "Réservé au réceptionniste et à l'administrateur.",
        responses={200: ReservationSerializer},
    )
    @action(detail=True, methods=['post'], url_path='checkin')
    def perform_checkin(self, request, pk=None):
        """Enregistrer le check-in — Réceptionniste/Admin."""
        reservation = self.get_object()

        if reservation.status != Reservation.Status.CONFIRMED:
            return Response(
                {
                    'error': (
                        f'Le check-in nécessite une réservation confirmée. '
                        f'Statut actuel: "{reservation.get_status_display()}".'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Créer ou mettre à jour l'enregistrement CheckIn
        checkin, created = CheckIn.objects.get_or_create(
            reservation=reservation,
            defaults={
                'receptionist': request.user,
                'notes': request.data.get('notes', ''),
            },
        )
        if not created:
            checkin.receptionist = request.user
            checkin.notes = request.data.get('notes', checkin.notes)

        checkin.checked_in_at = timezone.now()
        checkin.save()

        # Mettre à jour le statut de la réservation
        reservation.status = Reservation.Status.CHECKED_IN
        reservation.save()

        return Response(
            {
                'message': f'Check-in enregistré pour {reservation.client.get_full_name()}.',
                'reservation': ReservationSerializer(reservation, context={'request': request}).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Enregistrer le check-out",
        description="Enregistre le départ du client. "
                    "La réservation doit être en statut 'checked_in'. "
                    "Réservé au réceptionniste et à l'administrateur.",
        responses={200: ReservationSerializer},
    )
    @action(detail=True, methods=['post'], url_path='checkout')
    def perform_checkout(self, request, pk=None):
        """Enregistrer le check-out — Réceptionniste/Admin."""
        reservation = self.get_object()

        if reservation.status != Reservation.Status.CHECKED_IN:
            return Response(
                {
                    'error': (
                        f'Le check-out nécessite une réservation en statut "Arrivé". '
                        f'Statut actuel: "{reservation.get_status_display()}".'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mettre à jour l'enregistrement CheckIn
        try:
            checkin = reservation.checkin_record
            checkin.checked_out_at = timezone.now()
            if request.data.get('notes'):
                checkin.notes += f'\n[Check-out] {request.data["notes"]}'
            checkin.save()
        except CheckIn.DoesNotExist:
            CheckIn.objects.create(
                reservation=reservation,
                receptionist=request.user,
                checked_out_at=timezone.now(),
            )

        # Mettre à jour le statut de la réservation
        reservation.status = Reservation.Status.CHECKED_OUT
        reservation.save()

        # Libérer la chambre
        room = reservation.room
        room.status = 'cleaning'
        room.save()

        return Response(
            {
                'message': f'Check-out enregistré. Chambre {room.number} en nettoyage.',
                'reservation': ReservationSerializer(reservation, context={'request': request}).data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['payments'])
class PaymentViewSet(viewsets.ModelViewSet):
    """
    Gestion des paiements.

    **Permissions** :
    - Client : voit et crée ses propres paiements
    - Réceptionniste/Admin : voit tous les paiements
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.select_related('reservation', 'reservation__client')

        if user.role == 'client':
            queryset = queryset.filter(reservation__client=user)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Créer un paiement et le marquer comme complété."""
        serializer = PaymentCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        # Simuler la validation du paiement (en production: intégrer un gateway)
        payment.status = Payment.Status.COMPLETED
        payment.paid_at = timezone.now()
        payment.save()

        # Confirmer automatiquement la réservation après paiement
        reservation = payment.reservation
        if reservation.status == Reservation.Status.PENDING:
            reservation.status = Reservation.Status.CONFIRMED
            reservation.save()

        return Response(
            {
                'message': 'Paiement effectué avec succès ! Votre réservation est confirmée.',
                'payment': PaymentSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'La suppression d\'un paiement n\'est pas autorisée.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
