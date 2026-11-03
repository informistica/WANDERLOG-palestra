from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from boards.views import BoardViewSet
from places.views import BoardMapView, BoardPlaceViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'boards/(?P<board_pk>[^/.]+)/places', BoardPlaceViewSet,
                basename='board-place')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/boards/<uuid:board_pk>/map/', BoardMapView.as_view(), name='board-map-geojson'),
    path('api/v1/', include(router.urls)),
    # pagine HTML (livello 06)
    # TODO (passo 2): sostituisci con le URL di allauth
    path('accounts/', include('django.contrib.auth.urls')),
    # TODO (passo 9): la vista set_language di core
    path('boards/', include('boards.urls')),
    path('boards/', include('places.urls')),  # mappa (livello 07)
    path('', RedirectView.as_view(pattern_name='boards:list'), name='home'),
]

# TODO (passo 5): la pagina pubblica core/welcome.html con i18n_patterns (/it/ e /en/)
