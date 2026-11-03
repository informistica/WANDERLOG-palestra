"""Middleware di core: la lingua scelta dall'utente (livello 13)."""


class UserLanguageMiddleware:
    """TODO (passo 8): per l'utente autenticato attiva la lingua del suo profilo.

    Se user.language e' una delle LANGUAGES e il percorso non ha il prefisso /it/ o /en/,
    attiva la lingua (django.utils.translation.activate) e imposta request.LANGUAGE_CODE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)