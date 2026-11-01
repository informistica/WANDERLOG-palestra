"""Serializers per places."""
from rest_framework import serializers
from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    """TODO: Serializer per Place."""
    
    class Meta:
        model = Place
        fields = []  # TODO: ['id', 'name', 'lat', 'lng', 'description', 'board', 'created_at']
