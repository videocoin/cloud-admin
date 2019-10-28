from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Miner


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'current_stream_link')
    readonly_fields = ('id', 'current_stream_link')
    list_filter = ('status', )

    def current_stream_link(self, obj):
        if obj.current_task_id:
            return format_html('<a href="{}">{}</a>', reverse('admin:streams_stream_change', args=[obj.current_task_id]),
                               obj.current_task_id)
        return ''

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
