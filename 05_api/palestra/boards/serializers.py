"""Serializers per l'API boards."""
from rest_framework import serializers
from .models import Board, Collaborator


class BoardSerializer(serializers.ModelSerializer):
    """
    TODO: Serializer per Board.
    
    Campi da includere:
    - id, title, description, owner (read_only), created_at, updated_at
    """
    # TODO: Aggiungi owner come ReadOnlyField mostrando owner.email
    # owner = serializers.ReadOnlyField(source='owner.email')
    
    class Meta:
        model = Board
        # TODO: Specifica i fields
        fields = []  # TODO: ['id', 'title', 'description', 'owner', 'created_at', 'updated_at']
        # TODO: Aggiungi read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class CollaboratorSerializer(serializers.ModelSerializer):
    """TODO: Serializer per Collaborator."""
    
    class Meta:
        model = Collaborator
        fields = []  # TODO: Completa
