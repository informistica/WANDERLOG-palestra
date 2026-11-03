"""ViewSet dell'API delle bacheche: /api/v1/boards/."""
from rest_framework import status, viewsets  # noqa: F401
from rest_framework.decorators import action  # noqa: F401
from rest_framework.exceptions import PermissionDenied, ValidationError  # noqa: F401
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response  # noqa: F401

from .permissions import BoardPolicy
from .serializers import BoardSerializer, CollaboratorSerializer  # noqa: F401
from .services import add_collaborator, boards_visible_to, create_board  # noqa: F401


class BoardViewSet(viewsets.ModelViewSet):
    """Chi non può vedere una bacheca riceve 404; chi la vede ma non può modificarla, 403."""
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, BoardPolicy]

    def get_queryset(self):
        # TODO (passo 5): solo le bacheche visibili (boards_visible_to)
        raise NotImplementedError

    def perform_create(self, serializer):
        # TODO (passo 5): crea la bacheca con create_board(self.request.user, ...)
        #   e metti il risultato in serializer.instance;
        #   un ValueError del servizio diventa ValidationError (400)
        raise NotImplementedError

    # TODO (passo 5): azione POST /api/v1/boards/{id}/collaborators/
    #   @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    #   - board = self.get_object()  (404 se non visibile)
    #   - valida request.data con CollaboratorSerializer
    #   - chiama add_collaborator(..., requesting_user=request.user)
    #   - PermissionError -> PermissionDenied (403), ValueError -> ValidationError (400)
    #   - risposta 201 con il collaboratore serializzato
