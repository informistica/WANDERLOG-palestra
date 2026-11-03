"""Admin dell'app inbox."""
from django.contrib import admin

from .models import InboundAddress, InboundEmail


@admin.register(InboundAddress)
class InboundAddressAdmin(admin.ModelAdmin):
    list_display = ('token', 'board', 'created_at')
    search_fields = ('token', 'board__title')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(InboundEmail)
class InboundEmailAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'sender', 'subject', 'status', 'board', 'place')
    list_filter = ('status', 'created_at')
    search_fields = ('sender', 'subject', 'message_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
