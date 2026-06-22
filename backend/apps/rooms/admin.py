from django.contrib import admin
from .models import RoomCategory, Room, SeasonalRate


@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'max_occupancy', 'is_active', 'rooms_count']
    list_filter = ['is_active']
    search_fields = ['name']

    def rooms_count(self, obj):
        return obj.rooms.count()
    rooms_count.short_description = 'Nb chambres'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'category', 'floor', 'status', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'category', 'floor']
    search_fields = ['number', 'category__name']
    list_editable = ['status', 'is_active']


@admin.register(SeasonalRate)
class SeasonalRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'start_date', 'end_date', 'price_per_night']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    date_hierarchy = 'start_date'
