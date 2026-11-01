"""URL configuration."""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from boards.views import BoardViewSet
from places.views import PlaceViewSet

# TODO: Crea router DRF
router = routers.DefaultRouter()
# TODO: Registra BoardViewSet con basename='board'
# TODO: Registra PlaceViewSet con basename='place'

urlpatterns = [
    path('admin/', admin.site.urls),
    # TODO: Includi router sotto '/api/v1/'
    # path('api/v1/', include(router.urls)),
]
