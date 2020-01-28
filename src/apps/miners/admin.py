from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from django_mysql.models import JSONField
from jsoneditor.forms import JSONEditor
from prettyjson import PrettyJSONWidget

from common.admin import DontLog
from .models import Miner


class LocalityFilter(admin.SimpleListFilter):
    title = 'locality'
    parameter_name = 'locality'

    def lookups(self, request, model_admin):
        return (
            ('Internal', 'Internal'),
            ('External', 'External'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Internal':
            return queryset.filter(tags__contains={'locality': 'internal'})
        elif value == 'External':
            return queryset.exclude(tags__contains={'locality': 'internal'})
        return queryset


class MinerForm(forms.ModelForm):
    class Meta:
        model = Miner
        fields = '__all__'
        widgets = {
          'system_info': PrettyJSONWidget(attrs={'initial': 'parsed'}),
          'crypto_info': PrettyJSONWidget(attrs={'initial': 'parsed'}),
          'tags': JSONEditor(),
        }

    def __init__(self, *args, **kwargs):
        super(MinerForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['system_info'].widget.attrs['disabled'] = True
            self.fields['crypto_info'].widget.attrs['disabled'] = True


@admin.register(Miner)
class MinerAdmin(DontLog, admin.ModelAdmin):
    form = MinerForm

    list_filter = ('status', LocalityFilter,)

    list_display = (
        'id',
        'name',
        'status',
        'version',
        'owned_by',
        'task_assigned',
        'address',
        'cpu_freq',
        'cpu_cores', 
        'cpu_usage',
        'memory_total',
        'memory_used',
    )

    readonly_fields = (
        'id',
        'owned_by',
        'address',
        'task_assigned',
        'last_ping_at',
    )

    fieldsets = (
        ('Miner', {
            'fields': (
                'id',
                'name',
                'owned_by',
                'status',
                'current_task_id',
                'last_ping_at',
                'task_assigned',
                'address',
                'tags',
                'system_info',
                'crypto_info',
            )
        }),
    )

    class Media:
        css = {
            'all': ('admin.css',)
        }

    def owned_by(self, obj):
        if obj.by:
            url = resolve_url(admin_urlname(obj.by._meta, 'change'), obj.by.id)
            return format_html('<a href="{}">{}</a>', url, obj.by.email)
        return ''
    owned_by.short_description = 'Owner'
    owned_by.allow_tags = True

    def task_assigned(self, obj):
        if obj.current_task_id:
            url = reverse('admin:streams_task_change', args=[obj.current_task_id])
            return format_html('<a href="{}">{}</a>', url, obj.current_task_id)
        return ''
    task_assigned.short_description = 'Task'
    task_assigned.allow_tags = True

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
