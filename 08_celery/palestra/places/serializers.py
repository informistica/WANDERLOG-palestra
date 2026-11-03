"""Serializer dell'API dei luoghi."""
from rest_framework import serializers

from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'board', 'name', 'description', 'lat', 'lng', 'created_at']
        read_only_fields = ['id', 'board', 'created_at']
