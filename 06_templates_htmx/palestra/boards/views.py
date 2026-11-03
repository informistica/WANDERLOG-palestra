"""ViewSet dell'API delle bacheche: /api/v1/boards/."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import BoardPolicy
from .serializers import BoardSerializer, CollaboratorSerializer
from .services import add_collaborator, boards_visible_to, create_board


class BoardViewSet(viewsets.ModelViewSet):
    """Chi non può vedere una bacheca riceve 404; chi la vede ma non può modificarla, 403."""
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, BoardPolicy]

    def get_queryset(self):
        return boards_visible_to(self.request.user).select_related('owner')

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            serializer.instance = create_board(self.request.user, data.get('title'),
                                               data.get('description', ''))
        except ValueError as exc:
            raise ValidationError({'title': [str(exc)]})

    # Il permesso lo decide il servizio (policy can_add_collaborator), non BoardPolicy
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def collaborators(self, request, pk=None):
        board = self.get_object()
        serializer = CollaboratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            collaborator = add_collaborator(board, data['user'],
                                            data.get('role', 'viewer'),
                                            requesting_user=request.user)
        except PermissionError as exc:
            raise PermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError({'user': [str(exc)]})
        return Response(CollaboratorSerializer(collaborator).data,
                        status=status.HTTP_201_CREATED)
