"""Utilità per HTMX, senza pacchetti esterni (come in WANDERLOG: niente django-htmx)."""


def is_htmx(request):
    """True se la richiesta arriva da HTMX, cioè ha l'header `HX-Request: true`."""
    return request.headers.get('HX-Request') == 'true'
