from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.RoomCategoryViewSet, basename='room-category')
router.register(r'rates', views.SeasonalRateViewSet, basename='seasonal-rate')
router.register(r'', views.RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
]
