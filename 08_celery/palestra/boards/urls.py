"""URL delle pagine HTML delle bacheche (sotto /boards/)."""
from django.urls import path

from . import views_html

app_name = 'boards'

urlpatterns = [
    path('', views_html.board_list, name='list'),
    path('nuova/', views_html.board_create, name='create'),
    path('<uuid:pk>/', views_html.board_detail, name='detail'),
    path('<uuid:pk>/modifica/', views_html.board_edit, name='edit'),
]
