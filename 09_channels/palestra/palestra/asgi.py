"""Punto di ingresso ASGI: HTTP a Django, WebSocket a Channels."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'palestra.settings')
# Prima di tutto: carica le app di Django, poi si possono importare consumer e modelli
django_asgi_app = get_asgi_application()

# TODO (passo 5): un ProtocolTypeRouter: 'http' a django_asgi_app, 'websocket' a
#   AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))
#   con websocket_urlpatterns da boards.routing
application = django_asgi_app
