"""
URL configuration for HotelBookCI project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # API Auth (inscription, login, JWT refresh, profil)
    path('api/auth/', include('apps.accounts.urls')),

    # API Chambres (catégories, chambres, tarifs saisonniers)
    path('api/rooms/', include('apps.rooms.urls')),

    # API Réservations + Paiements + Check-in/out
    path('api/', include('apps.reservations.urls')),

    # ---- Swagger / OpenAPI ----
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
