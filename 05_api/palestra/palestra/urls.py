from django.contrib import admin
from django.urls import path

# TODO (passo 7): crea un DefaultRouter di DRF e registra
#   - BoardViewSet (boards/views.py) sul prefisso 'boards', basename 'board'
#   - BoardPlaceViewSet (places/views.py) sul prefisso annidato
#     r'boards/(?P<board_pk>[^/.]+)/places', basename 'board-place'
#   poi includi le sue URL sotto 'api/v1/' (django.urls.include)

urlpatterns = [
    path('admin/', admin.site.urls),
]
