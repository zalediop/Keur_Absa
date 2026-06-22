"""
Serializers pour l'app reservations.
"""
from datetime import date
from rest_framework import serializers
from .models import Reservation, Payment, CheckIn
from apps.rooms.serializers import RoomSerializer
from apps.accounts.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'reservation', 'amount', 'method',
            'status', 'transaction_id', 'paid_at', 'created_at',
        ]
        read_only_fields = ['transaction_id', 'created_at']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Sérialisation pour la création d'un paiement."""
    class Meta:
        model = Payment
        fields = ['reservation', 'amount', 'method']

    def validate_reservation(self, reservation):
        # Vérifier que la réservation appartient au client connecté
        request = self.context.get('request')
        if request and reservation.client != request.user:
            if request.user.role not in ['admin']:
                raise serializers.ValidationError(
                    "Vous ne pouvez payer que vos propres réservations."
                )
        # Vérifier qu'il n'y a pas déjà un paiement complété
        if hasattr(reservation, 'payment') and reservation.payment.status == 'completed':
            raise serializers.ValidationError(
                "Cette réservation est déjà payée."
            )
        return reservation


class CheckInSerializer(serializers.ModelSerializer):
    receptionist_name = serializers.CharField(
        source='receptionist.get_full_name',
        read_only=True,
    )

    class Meta:
        model = CheckIn
        fields = [
            'id', 'reservation', 'receptionist', 'receptionist_name',
            'checked_in_at', 'checked_out_at', 'notes', 'created_at',
        ]
        read_only_fields = ['receptionist', 'created_at']


class ReservationSerializer(serializers.ModelSerializer):
    """Sérialisation complète d'une réservation (lecture)."""
    client_detail = UserSerializer(source='client', read_only=True)
    room_detail = RoomSerializer(source='room', read_only=True)
    payment = PaymentSerializer(read_only=True)
    checkin_record = CheckInSerializer(read_only=True)
    nights = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_cancellable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'client', 'client_detail', 'room', 'room_detail',
            'check_in_date', 'check_out_date', 'nights',
            'adults', 'children', 'status', 'status_display',
            'total_price', 'special_requests',
            'is_cancellable', 'payment', 'checkin_record',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['client', 'total_price', 'status', 'created_at', 'updated_at']
        extra_kwargs = {
            'room': {'write_only': True},
        }


class ReservationCreateSerializer(serializers.ModelSerializer):
    """
    Sérialisation pour la création d'une réservation.

    Le client est automatiquement défini sur l'utilisateur connecté.
    Le prix total est calculé automatiquement.
    """

    class Meta:
        model = Reservation
        fields = [
            'room', 'check_in_date', 'check_out_date',
            'adults', 'children', 'special_requests',
        ]

    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        room = data.get('room')

        # Vérifier les dates
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError(
                    {'check_out_date': 'La date de départ doit être postérieure à la date d\'arrivée.'}
                )
            if check_in < date.today():
                raise serializers.ValidationError(
                    {'check_in_date': 'La date d\'arrivée ne peut pas être dans le passé.'}
                )

        # Vérifier la disponibilité de la chambre
        if room and check_in and check_out:
            overlapping = Reservation.objects.filter(
                room=room,
                status__in=['pending', 'confirmed', 'checked_in'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
            )
            # Exclure la réservation en cours d'édition si applicable
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    {'room': 'Cette chambre n\'est pas disponible pour les dates sélectionnées.'}
                )

            # Vérifier que la chambre n'est pas en maintenance
            if room.status == 'maintenance':
                raise serializers.ValidationError(
                    {'room': 'Cette chambre est actuellement en maintenance.'}
                )

        # Vérifier la capacité
        room = data.get('room')
        adults = data.get('adults', 1)
        children = data.get('children', 0)
        if room and (adults + children) > room.category.max_occupancy:
            raise serializers.ValidationError(
                {
                    'adults': (
                        f'Le nombre de personnes ({adults + children}) dépasse la capacité '
                        f'de la chambre ({room.category.max_occupancy}).'
                    )
                }
            )

        return data

    def create(self, validated_data):
        request = self.context['request']
        room = validated_data['room']
        check_in = validated_data['check_in_date']
        check_out = validated_data['check_out_date']

        # Calcul automatique du prix total
        nights = (check_out - check_in).days
        price_per_night = room.get_current_price(check_in)
        total_price = price_per_night * nights

        reservation = Reservation.objects.create(
            client=request.user,
            total_price=total_price,
            **validated_data,
        )
        return reservation
