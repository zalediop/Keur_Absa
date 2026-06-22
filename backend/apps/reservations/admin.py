from django.contrib import admin
from .models import Reservation, Payment, CheckIn


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'room', 'check_in_date', 'check_out_date',
        'nights', 'status', 'total_price', 'created_at',
    ]
    list_filter = ['status', 'check_in_date', 'created_at']
    search_fields = ['client__username', 'client__email', 'room__number']
    date_hierarchy = 'check_in_date'
    readonly_fields = ['total_price', 'created_at', 'updated_at']

    def nights(self, obj):
        return obj.nights
    nights.short_description = 'Nuits'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reservation', 'amount', 'method', 'status',
        'transaction_id', 'paid_at',
    ]
    list_filter = ['status', 'method']
    search_fields = ['transaction_id', 'reservation__client__username']
    readonly_fields = ['transaction_id', 'created_at']


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reservation', 'receptionist',
        'checked_in_at', 'checked_out_at',
    ]
    search_fields = ['reservation__client__username', 'receptionist__username']
