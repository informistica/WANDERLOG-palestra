"""Admin per bacheche e utenti."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Board


# TODO: Personalizza UserAdmin per il modello User senza username
# Suggerimento: list_display, fieldsets, add_fieldsets, ordering
# class UserAdmin(BaseUserAdmin):
#     ...

# TODO: Registra User con UserAdmin personalizzato
# admin.site.register(User, UserAdmin)

# TODO: Registra Board con l'admin di default
# admin.site.register(Board)
