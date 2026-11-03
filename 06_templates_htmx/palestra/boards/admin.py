"""Admin per bacheche e utenti."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Board, Collaborator


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizzato per User senza username."""
    list_display = ('email', 'name', 'language', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'language')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informazioni personali', {'fields': ('name', 'language')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Date importanti', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin per Board."""
    list_display = ('title', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'owner__email')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    """Admin per Collaborator."""
    list_display = ('user', 'board', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'board__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
