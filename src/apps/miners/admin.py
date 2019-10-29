from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Miner


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'current_stream_link', 'cpu_freq',  'cpu_cores',  'load1',  'load5',  'load15',
                    'memory_free',  'memory_used',  'memory_total', 'cpu_percent_sys', 'cpu_percent_idle',
                    'cpu_percent_intr', 'cpu_percent_nice', 'cpu_percent_user', 'cpu_percent_states')

    readonly_fields = ('id', 'current_stream_link', 'cpu_freq',  'cpu_cores',  'load1',  'load5',  'load15',
                       'memory_free',  'memory_used',  'memory_total', 'cpu_percent_sys', 'cpu_percent_idle',
                       'cpu_percent_intr', 'cpu_percent_nice', 'cpu_percent_user', 'cpu_percent_states')
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
