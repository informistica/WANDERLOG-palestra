"""Views API per boards."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Board
from .serializers import BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """
    TODO: ViewSet per Board.
    
    Deve:
    - Filtrare boards per user (owner o collaborator)
    - Impostare owner automaticamente alla creazione
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # TODO: Ritorna solo boards dove user è owner o collaborator
        # Usa Q objects: Q(owner=self.request.user) | Q(collaborators__user=self.request.user)
        return Board.objects.none()  # TODO: Fix
    
    def perform_create(self, serializer):
        # TODO: Salva con owner=self.request.user
        pass
