"""Paginazione comune a tutte le API del progetto."""
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """20 elementi per pagina; il client può chiederne fino a 100 con ?page_size=."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
