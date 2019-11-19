from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from django_mysql.models import JSONField
from jsoneditor.forms import JSONEditor

from common.admin import DontLog
from .models import Miner


@admin.register(Miner)
class MinerAdmin(DontLog, admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    list_display = (
        'id', 'name', 'user', 'status', 'current_stream_link', 'version', 'internal', 'cpu_freq', 'cpu_cores',  'cpu_usage',
        'memory_total', 'memory_used', 'address'
    )
    readonly_fields = (
        'id', 'user', 'status', 'address', 'current_task_id', 'cpu_freq', 'cpu_cores',  'cpu_usage', 'memory_total', 'memory_used', 'user_id', 'last_ping_at',
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

    def internal(self, instance):
        return instance.internal
    internal.boolean = True

    def cpu_freq(self, instance):
        return instance.cpu_freq
    cpu_freq.short_description = 'CPU Freq (MHz)'
    cpu_freq.admin_order_field = 'system_info__cpu__freq'

    def cpu_usage(self, instance):
        return instance.cpu_usage
    cpu_usage.short_description = 'CPU Usage (%)'
    cpu_usage.admin_order_field = 'system_info__cpu_usage'

    def memory_total(self, instance):
        return instance.memory_total
    memory_total.short_description = 'Memory total (GB)'
    memory_total.admin_order_field = 'system_info__memory__total'

    def memory_used(self, instance):
        return instance.memory_used
    memory_used.short_description = 'Memory used (GB)'
    memory_used.admin_order_field = 'system_info__memory__used'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
