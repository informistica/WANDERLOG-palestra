"""Admin per bacheche e utenti."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Board, Collaborator


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'language', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'language')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informazioni', {'fields': ('name', 'language')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'name', 'password1', 'password2')}),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'owner__email')


# TODO: Registra Collaborator con admin.site.register
