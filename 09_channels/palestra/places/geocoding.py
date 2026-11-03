"""Adapter di geocodifica inversa (coordinate -> indirizzo).

Come gli adapter di WANDERLOG ha un'implementazione `mock` deterministica, usata in sviluppo
e nei test. Un provider vero farebbe una richiesta HTTP che puo' fallire: in quel caso
solleva GeocodingError, un errore temporaneo che il task puo' ritentare.
"""


class GeocodingError(Exception):
    """Errore temporaneo del provider (rete, limite di richieste): si puo' ritentare."""


def reverse_geocode(lat, lng):
    """Restituisce un indirizzo leggibile per le coordinate."""
    return f'Indirizzo simulato ({lat:.4f}, {lng:.4f})'
