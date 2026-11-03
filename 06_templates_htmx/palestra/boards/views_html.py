"""Pagine HTML delle bacheche: template Django + partial HTMX.

Le view usano le stesse policy e gli stessi servizi dell'API (livelli 04-05):
chi non vede la bacheca riceve 404, chi la vede ma non può modificarla 403.
"""
from django.contrib.auth.decorators import login_required  # noqa: F401
from django.core.exceptions import PermissionDenied  # noqa: F401
from django.shortcuts import get_object_or_404, redirect, render  # noqa: F401
from django.views.decorators.http import require_POST  # noqa: F401

from core.htmx import is_htmx  # noqa: F401

from .forms import BoardForm  # noqa: F401
from .policies import can_edit_board  # noqa: F401
from .services import boards_visible_to, create_board, update_board  # noqa: F401


def _retarget(response, selector):
    """Con un form non valido HTMX deve sostituire il form, non il bersaglio di successo."""
    response['HX-Retarget'] = selector
    response['HX-Reswap'] = 'outerHTML'
    return response


# TODO (passo 6): tutte le view richiedono il login (@login_required);
#   board_create e board_edit accettano solo POST (@require_POST)

def board_list(request):
    # TODO (passo 6): bacheche visibili (boards_visible_to).
    #   Con HTMX: solo il partial boards/_board_list.html;
    #   senza: la pagina boards/board_list.html con anche un BoardForm vuoto
    raise NotImplementedError


def board_create(request):
    # TODO (passo 6): valida BoardForm(request.POST) e crea con create_board(request.user, ...)
    #   - successo con HTMX: il partial della lista aggiornata; senza HTMX: redirect alla lista
    #   - errori con HTMX: il partial del form con _retarget(..., '#board-form');
    #     senza HTMX: la pagina della lista con il form e i suoi errori
    raise NotImplementedError


def board_detail(request, pk):
    # TODO (passo 7): get_object_or_404 sulle bacheche visibili (estraneo -> 404).
    #   Contesto: board, places, can_edit (can_edit_board) e, solo per chi può
    #   modificare, form = BoardForm con i valori attuali come initial
    raise NotImplementedError


def board_edit(request, pk):
    # TODO (passo 7): bacheca visibile (altrimenti 404); chi non può modificarla -> 403
    #   (PermissionDenied). Valida BoardForm(request.POST) SENZA instance e salva con
    #   update_board(..., requesting_user=request.user)
    #   - successo con HTMX: partial boards/_board_header.html; senza: redirect al dettaglio
    #   - errori con HTMX: partial del form di modifica con _retarget(..., '#board-edit-form')
    raise NotImplementedError
