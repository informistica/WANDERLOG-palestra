"""Pagine HTML dell'app places (livello 07)."""
from django.urls import path

from . import views_html

app_name = 'places'

urlpatterns = [
    path('<uuid:board_pk>/mappa/', views_html.board_map, name='board-map'),
]
