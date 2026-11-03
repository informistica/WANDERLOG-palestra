"""Pagine HTML delle bacheche: template Django + partial HTMX.

Le view usano le stesse policy e gli stessi servizi dell'API (livelli 04-05):
chi non vede la bacheca riceve 404, chi la vede ma non può modificarla 403.
"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.htmx import is_htmx

from .forms import BoardForm
from .policies import can_edit_board
from .services import boards_visible_to, create_board, update_board


def _visible_boards(request):
    return boards_visible_to(request.user).select_related('owner')


def _retarget(response, selector):
    """Con un form non valido HTMX deve sostituire il form, non il bersaglio di successo."""
    response['HX-Retarget'] = selector
    response['HX-Reswap'] = 'outerHTML'
    return response


@login_required
def board_list(request):
    boards = _visible_boards(request)
    if is_htmx(request):
        return render(request, 'boards/_board_list.html', {'boards': boards})
    return render(request, 'boards/board_list.html', {'boards': boards, 'form': BoardForm()})


@login_required
@require_POST
def board_create(request):
    form = BoardForm(request.POST)
    if form.is_valid():
        try:
            create_board(request.user, form.cleaned_data['title'],
                         form.cleaned_data['description'])
        except ValueError as exc:
            form.add_error('title', str(exc))
    if form.errors:
        if is_htmx(request):
            return _retarget(render(request, 'boards/_board_form.html', {'form': form}),
                             '#board-form')
        return render(request, 'boards/board_list.html',
                      {'boards': _visible_boards(request), 'form': form})
    if is_htmx(request):
        return render(request, 'boards/_board_list.html', {'boards': _visible_boards(request)})
    return redirect('boards:list')


def _detail_context(request, board, form=None):
    can_edit = can_edit_board(request.user, board)
    if can_edit and form is None:
        form = BoardForm(initial={'title': board.title, 'description': board.description})
    return {'board': board, 'can_edit': can_edit, 'form': form,
            'places': board.places.all()}


@login_required
def board_detail(request, pk):
    board = get_object_or_404(_visible_boards(request), pk=pk)
    return render(request, 'boards/board_detail.html', _detail_context(request, board))


@login_required
@require_POST
def board_edit(request, pk):
    board = get_object_or_404(_visible_boards(request), pk=pk)
    if not can_edit_board(request.user, board):
        raise PermissionDenied("Solo il proprietario può modificare la bacheca")
    form = BoardForm(request.POST)  # senza instance: is_valid() non deve toccare board
    if form.is_valid():
        try:
            update_board(board, form.cleaned_data['title'], form.cleaned_data['description'],
                         requesting_user=request.user)
        except PermissionError as exc:
            raise PermissionDenied(str(exc))
        except ValueError as exc:
            form.add_error('title', str(exc))
    if form.errors:
        if is_htmx(request):
            return _retarget(render(request, 'boards/_board_edit_form.html',
                                    {'board': board, 'form': form}), '#board-edit-form')
        return render(request, 'boards/board_detail.html',
                      _detail_context(request, board, form))
    if is_htmx(request):
        return render(request, 'boards/_board_header.html', {'board': board})
    return redirect('boards:detail', pk=board.pk)
