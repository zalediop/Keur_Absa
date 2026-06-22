from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration personnalisée du modèle User."""

    list_display = ['username', 'email', 'get_full_name', 'role', 'phone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations HotelBookCI', {
            'fields': ('role', 'phone', 'address', 'avatar'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations HotelBookCI', {
            'fields': ('role', 'email', 'first_name', 'last_name', 'phone'),
        }),
    )
