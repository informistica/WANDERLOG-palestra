"""URL configuration."""
from django.contrib import admin
from django.urls import path
from boards import views as boards_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('boards/', boards_views.board_list, name='board_list'),
    path('boards/create/', boards_views.board_create, name='board_create'),
    path('boards/<uuid:pk>/delete/', boards_views.board_delete, name='board_delete'),
]
