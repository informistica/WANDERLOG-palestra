"""Serializer dell'API dei luoghi."""
from rest_framework import serializers

from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        # TODO (passo 4): id, board, name, description, lat, lng, created_at
        #   board, id e created_at in sola lettura (la bacheca arriva dall'URL)
        fields = ['id']
        read_only_fields = ['id']
