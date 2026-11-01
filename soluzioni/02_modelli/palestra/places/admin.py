"""Admin per luoghi."""
from django.contrib import admin
from .models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    """Admin per Place."""
    list_display = ('name', 'board', 'lat', 'lng', 'created_at')
    list_filter = ('created_at', 'board')
    search_fields = ('name', 'description', 'board__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
