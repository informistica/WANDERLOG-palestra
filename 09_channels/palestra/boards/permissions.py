"""Permission class DRF: traducono le policy di boards/policies.py per l'API."""
from rest_framework import permissions

from .policies import can_edit_board, can_view_board


class BoardPolicy(permissions.BasePermission):
    """Lettura a proprietario e collaboratori, scrittura solo al proprietario."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return can_view_board(request.user, obj)
        return can_edit_board(request.user, obj)
