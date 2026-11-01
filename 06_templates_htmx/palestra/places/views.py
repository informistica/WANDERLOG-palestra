"""Views API per places."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Place
from .serializers import PlaceSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    """TODO: ViewSet per Place."""
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # TODO: Filtra places delle boards accessibili all'utente
        return Place.objects.none()  # TODO: Fix
