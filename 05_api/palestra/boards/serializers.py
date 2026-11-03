"""Serializer dell'API delle bacheche."""
from rest_framework import serializers

from .models import Board, Collaborator, User  # noqa: F401


class BoardSerializer(serializers.ModelSerializer):
    # TODO (passo 4): owner = email del proprietario, in sola lettura
    #   (serializers.SlugRelatedField con slug_field='email' e read_only=True)

    class Meta:
        model = Board
        # TODO (passo 4): id, title, description, owner, created_at, updated_at
        fields = ['id']
        read_only_fields = ['id']


class CollaboratorSerializer(serializers.ModelSerializer):
    # TODO (passo 4): user = email dell'utente, in lettura e scrittura
    #   (SlugRelatedField con slug_field='email' e queryset=User.objects.all())

    class Meta:
        model = Collaborator
        # TODO (passo 4): id, user, role, created_at
        fields = ['id']
        read_only_fields = ['id']
