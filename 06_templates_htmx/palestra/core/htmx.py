"""Utilità per HTMX, senza pacchetti esterni (come in WANDERLOG: niente django-htmx)."""


def is_htmx(request):
    """True se la richiesta arriva da HTMX, cioè ha l'header `HX-Request: true`."""
    # TODO (passo 2): leggi l'header da request.headers; True solo se vale 'true'
    raise NotImplementedError
