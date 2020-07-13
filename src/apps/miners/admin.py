from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from jsoneditor.forms import JSONEditor
from prettyjson import PrettyJSONWidget

from common.admin import DeletedFilter
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
          'tags': JSONEditor(),
        }

    def __init__(self, *args, **kwargs):
        super(MinerForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['system_info'].widget.attrs['disabled'] = True


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    form = MinerForm

    list_filter = (DeletedFilter, 'status', 'is_internal', 'is_lock', 'is_block')

    list_display = (
        'id',
        'name',
        'status',
        'version',
        'owned_by',
        'task_assigned',
        'is_internal',
        'hostname',
        'is_lock',
        'is_block',
    )

    readonly_fields = (
        'id',
        'owned_by',
        'address',
        'last_ping_at',
        'deleted_at',
        'reward',
    )

    fieldsets = (
        ('Miner', {
            'fields': (
                'id',
                'name',
                'owned_by',
                'status',
                'is_internal',
                'is_lock',
                'is_block',
                'current_task_id',
                'last_ping_at',
                'address',
                'tags',
                'system_info',
                'worker_info',
                'deleted_at',
                'access_key',
                'key',
                'secret',
                'reward',
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

    def hostname(self, instance):
        return instance.hostname
    hostname.short_description = 'Hostname'
    hostname.admin_order_field = 'system_info__host__hostname'

    def has_add_permission(self, request):
        return False
