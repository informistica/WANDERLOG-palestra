"""API dei luoghi di una bacheca: /api/v1/boards/{board_pk}/places/."""
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError  # noqa: F401
from rest_framework.generics import get_object_or_404  # noqa: F401
from rest_framework.permissions import IsAuthenticated

from boards.policies import can_edit_board  # noqa: F401
from boards.services import boards_visible_to  # noqa: F401

from .models import Place  # noqa: F401
from .serializers import PlaceSerializer
from .services import add_place_to_board  # noqa: F401


class BoardPlaceViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_board(self):
        """La bacheca dell'URL, solo se visibile all'utente (altrimenti 404)."""
        # TODO (passo 6): get_object_or_404(boards_visible_to(...), pk=self.kwargs['board_pk'])
        raise NotImplementedError

    def get_queryset(self):
        # TODO (passo 6): i luoghi della bacheca di get_board()
        raise NotImplementedError

    def perform_create(self, serializer):
        # TODO (passo 6): solo chi può modificare la bacheca (can_edit_board), altrimenti
        #   PermissionDenied (403); crea il luogo con add_place_to_board e metti il
        #   risultato in serializer.instance; ValueError -> ValidationError (400)
        raise NotImplementedError

    def perform_destroy(self, instance):
        # TODO (passo 6): stesso controllo di perform_create, poi instance.delete()
        raise NotImplementedError
