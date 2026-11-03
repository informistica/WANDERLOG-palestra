"""Serializer dell'API delle bacheche."""
from rest_framework import serializers

from .models import Board, Collaborator, User


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CollaboratorSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = Collaborator
        fields = ['id', 'user', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']
