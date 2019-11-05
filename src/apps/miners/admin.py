from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse

from .models import Miner


class MinerForm(forms.ModelForm):
    tags_internal_field = forms.BooleanField(label='tags: internal', required=False)
    tags_force_task_id_field = forms.CharField(label='tags: force task_id',  max_length=255, min_length=1, required=False)

    class Meta:
        model = Miner
        fields = ('current_task_id', 'tags_internal_field', 'tags_force_task_id_field')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['tags_internal_field'] = self.instance.tags_internal
        self.initial['tags_force_task_id_field'] = self.instance.tags_force_task_id

    def save(self, commit=True):
        if 'tags_internal_field' in self.cleaned_data:
            self.instance.set_tag('internal', self.cleaned_data['tags_internal_field'])
        if 'tags_force_task_id_field' in self.cleaned_data:
            self.instance.set_tag('force_task_id', self.cleaned_data['tags_force_task_id_field'])
        return super().save(commit=commit)


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    form = MinerForm
    list_display = (
        'id', 'status', 'current_stream_link', 'version', 'cpu_freq', 'cpu_cores',  'cpu_usage',
        'memory_total', 'memory_used', 'tags_force_task_id', 'tags_internal'
    )
    readonly_fields = (
        'id', 'cpu_freq', 'cpu_cores',  'cpu_usage', 'memory_total', 'memory_used', 'user_id', 'last_ping_at',
        'system_info', 'tags_force_task_id', 'tags_internal'
    )
    list_filter = ('status', )

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
