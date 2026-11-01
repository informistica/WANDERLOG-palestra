"""Views per boards con template e HTMX."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Board
from .forms import BoardForm
from .policies import can_view_board, can_edit_board


@login_required
def board_list(request):
    """
    Lista boards dell'utente.
    TODO: Filtra boards per owner o collaborator.
    TODO: Se request.headers.get('HX-Request'), renderizza solo il partial.
    """
    boards = Board.objects.all()  # TODO: Filtrare per user
    
    # TODO: Implementa logica HX-Request
    # if request.headers.get('HX-Request'):
    #     return render(request, 'boards/board_list_partial.html', {'boards': boards})
    
    return render(request, 'boards/board_list.html', {'boards': boards})


@login_required
def board_create(request):
    """
    Crea una nuova board.
    TODO: Se POST con errori e HX-Request, renderizza solo form partial con errori.
    """
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            # TODO: Con HTMX, ritorna partial invece di redirect
            return redirect('board_list')
        else:
            # TODO: Se HX-Request, renderizza partial del form con errori
            pass
    else:
        form = BoardForm()
    
    return render(request, 'boards/board_form.html', {'form': form})


@login_required
def board_delete(request, pk):
    """
    Cancella board.
    TODO: Controlla permessi con can_edit_board (riusa da policies.py livello 04).
    """
    board = get_object_or_404(Board, pk=pk)
    
    # TODO: Aggiungi controllo permessi
    # if not can_edit_board(request.user, board):
    #     return HttpResponseForbidden("Non hai i permessi")
    
    if request.method == 'POST':
        board.delete()
        return redirect('board_list')
    
    return render(request, 'boards/board_confirm_delete.html', {'board': board})
