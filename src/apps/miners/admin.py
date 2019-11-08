from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from django_mysql.models import JSONField
from jsoneditor.forms import JSONEditor

from .models import Miner


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    list_display = (
        'id', 'status', 'current_stream_link', 'version', 'internal', 'cpu_freq', 'cpu_cores',  'cpu_usage',
        'memory_total', 'memory_used'
    )
    readonly_fields = (
        'id', 'cpu_freq', 'cpu_cores',  'cpu_usage', 'memory_total', 'memory_used', 'user_id', 'last_ping_at',
        'system_info', 'internal'
    )
    list_filter = ('status', )

    class Media:
        css = {
            'all': ('admin.css',)
        }

    def current_stream_link(self, obj):
        if obj.current_task_id:
            return format_html('<a href="{}">{}</a>', reverse('admin:streams_stream_change', args=[obj.current_task_id]),
                               obj.current_task_id)
        return ''

    current_stream_link.short_description = 'Stream'
    current_stream_link.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
