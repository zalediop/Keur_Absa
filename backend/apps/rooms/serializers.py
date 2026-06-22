"""
Serializers pour l'app rooms.
"""
from rest_framework import serializers
from .models import RoomCategory, Room, SeasonalRate


class SeasonalRateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SeasonalRate
        fields = [
            'id', 'category', 'category_name', 'name',
            'start_date', 'end_date', 'price_per_night',
        ]

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    'La date de début doit être antérieure à la date de fin.'
                )
        return data


class RoomCategorySerializer(serializers.ModelSerializer):
    """Sérialisation d'une catégorie de chambre avec ses tarifs saisonniers."""
    seasonal_rates = SeasonalRateSerializer(many=True, read_only=True)
    rooms_count = serializers.SerializerMethodField()

    class Meta:
        model = RoomCategory
        fields = [
            'id', 'name', 'description', 'max_occupancy',
            'base_price', 'amenities', 'image', 'is_active',
            'rooms_count', 'seasonal_rates',
        ]

    def get_rooms_count(self, obj):
        return obj.rooms.filter(is_active=True).count()


class RoomCategoryLiteSerializer(serializers.ModelSerializer):
    """Version légère sans tarifs — pour les listes de chambres."""
    class Meta:
        model = RoomCategory
        fields = ['id', 'name', 'base_price', 'max_occupancy', 'amenities', 'image']


class RoomSerializer(serializers.ModelSerializer):
    """
    Sérialisation complète d'une chambre.
    Inclut la catégorie et le prix applicable aujourd'hui.
    """
    category_detail = RoomCategoryLiteSerializer(source='category', read_only=True)
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id', 'number', 'floor', 'category', 'category_detail',
            'status', 'description', 'image', 'is_active',
            'current_price', 'created_at',
        ]
        extra_kwargs = {
            'category': {'write_only': True},
        }

    def get_current_price(self, obj):
        """Retourne le prix applicable à la date de check-in demandée (ou aujourd'hui)."""
        check_in = self.context.get('check_in')
        if check_in:
            from datetime import datetime
            try:
                date = datetime.strptime(str(check_in), '%Y-%m-%d').date()
                return float(obj.get_current_price(date))
            except (ValueError, TypeError):
                pass
        return float(obj.get_current_price())


class RoomAvailabilitySerializer(serializers.ModelSerializer):
    """
    Chambre avec disponibilité calculée pour une période donnée.
    Utilisé par la vue de recherche de chambres disponibles.
    """
    category_detail = RoomCategoryLiteSerializer(source='category', read_only=True)
    price_for_period = serializers.SerializerMethodField()
    nights = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id', 'number', 'floor', 'category_detail',
            'status', 'description', 'image',
            'price_for_period', 'nights',
        ]

    def get_price_for_period(self, obj):
        check_in = self.context.get('check_in')
        check_out = self.context.get('check_out')
        if check_in and check_out:
            from datetime import datetime
            try:
                ci = datetime.strptime(str(check_in), '%Y-%m-%d').date()
                co = datetime.strptime(str(check_out), '%Y-%m-%d').date()
                nights = (co - ci).days
                price = float(obj.get_current_price(ci))
                return round(price * nights, 2)
            except (ValueError, TypeError):
                pass
        return float(obj.get_current_price())

    def get_nights(self, obj):
        check_in = self.context.get('check_in')
        check_out = self.context.get('check_out')
        if check_in and check_out:
            from datetime import datetime
            try:
                ci = datetime.strptime(str(check_in), '%Y-%m-%d').date()
                co = datetime.strptime(str(check_out), '%Y-%m-%d').date()
                return (co - ci).days
            except (ValueError, TypeError):
                pass
        return None
