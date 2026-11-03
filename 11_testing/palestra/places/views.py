"""API dei luoghi di una bacheca: /api/v1/boards/{board_pk}/places/ e .../map/."""
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards.policies import can_edit_board
from boards.services import boards_visible_to

from .models import Place
from .serializers import PlaceSerializer
from .services import add_place_to_board, board_geojson


class BoardPlaceViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_board(self):
        """La bacheca dell'URL, solo se visibile all'utente (altrimenti 404)."""
        if not hasattr(self, '_board'):
            self._board = get_object_or_404(boards_visible_to(self.request.user),
                                            pk=self.kwargs['board_pk'])
        return self._board

    def get_queryset(self):
        return Place.objects.filter(board=self.get_board())

    def _require_edit(self):
        if not can_edit_board(self.request.user, self.get_board()):
            raise PermissionDenied("Solo il proprietario può modificare i luoghi")

    def perform_create(self, serializer):
        self._require_edit()
        data = serializer.validated_data
        try:
            serializer.instance = add_place_to_board(
                self.get_board(), data['name'], data['lat'], data['lng'],
                data.get('description', ''))
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)})

    def perform_destroy(self, instance):
        self._require_edit()
        instance.delete()


class BoardMapView(APIView):
    """GeoJSON dei luoghi di una bacheca per l'isola della mappa: /api/v1/boards/{board_pk}/map/.

    Stesse regole del resto dell'API: login obbligatorio, estraneo 404, chi vede la bacheca
    vede anche la mappa.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, board_pk):
        board = get_object_or_404(boards_visible_to(request.user), pk=board_pk)
        return Response(board_geojson(board))
