"""Permission class DRF: traducono le policy di boards/policies.py per l'API."""
from rest_framework import permissions

from .policies import can_edit_board, can_view_board  # noqa: F401


class BoardPolicy(permissions.BasePermission):
    """Lettura a proprietario e collaboratori, scrittura solo al proprietario."""

    def has_object_permission(self, request, view, obj):
        # TODO (passo 3): metodi sicuri (permissions.SAFE_METHODS) -> can_view_board
        # TODO (passo 3): tutti gli altri -> can_edit_board
        raise NotImplementedError
