import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, resolve_url
from django.utils.html import format_html
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from common.admin import DontLog
from github.com.videocoin.cloud_api.streams.private.v1.client import StreamsServiceClient

from .models import Stream


@admin.register(Stream)
class StreamAdmin(DontLog, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'owned_by',
        'profile_set',
        'status',
        'input_status',
        'get_input_url',
        'get_output_url',
        'created_at',
        'ready_at',
        'completed_at',
    )

    list_filter = (
        'status',
        'input_status',
        'created_at',
        'ready_at',
        'completed_at',
    )

    readonly_fields = (
        'id',
        'profile_set',
        'status',
        'refunded',
        'input_status',
        'stream_contract_id',
        'stream_contract_address',
        'get_input_url',
        'get_output_url',
        'get_rtmp_url',
        'task_id',
        'task_status',
        'task_cmdline',
        'task_input',
        'task_output',
        'task_client_id',
        'created_at',
        'ready_at',
        'updated_at',
        'completed_at',
        'owned_by',
    )

    change_form_template = 'admin/streams/stream_change_form.html'
    search_fields = ('id', 'name')

    fieldsets = (
        ('Stream', {
            'fields': (
                'id',
                'name',
                'status',
                'input_status',
                'profile_set',
                'stream_contract_id',
                'stream_contract_address',
                'owned_by',
            )
        }),
        ('Stream urls', {
            'fields': (
                'get_input_url',
                'get_output_url',
                'get_rtmp_url',
            )
        }),
        ('Stream dates', {
            'fields': (
                'created_at',
                'updated_at',
                'ready_at',
                'completed_at',
            )
        }),
        ('Task', {
            'fields': (
                'task_status',
                'task_cmdline',
                'task_input',
                'task_output',
                'task_client_id',
            )
        }),
    )

    def profile_set(self, obj):
        if obj.profile:
            url = resolve_url(admin_urlname(obj.profile._meta, 'change'), obj.profile.id)
            return format_html('<a href="{}">{}</a>', url, obj.profile.name)
        return ''
    profile_set.short_description = 'Profile'
    profile_set.allow_tags = True

    def owned_by(self, obj):
        if obj.by:
            url = resolve_url(admin_urlname(obj.by._meta, 'change'), obj.by.id)
            return format_html('<a href="{}">{}</a>', url, obj.by.email)
        return ''
    owned_by.short_description = 'By'
    owned_by.allow_tags = True

    def get_rtmp_url(self, obj):
         return format_html('<a target="_blank" href="{}" />Link</a>', obj.rtmp_url)
    get_rtmp_url.short_description = "RTMP"

    def get_input_url(self, obj):
         return format_html('<a target="_blank" href="{}" />Link</a>', obj.input_url)
    get_input_url.short_description = "Input"

    def get_output_url(self, obj):
         return format_html('<a target="_blank" href="{}" />Link</a>', obj.output_url)
    get_output_url.short_description = "Output"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/start/', self.start_stream, name='streams_stream_start'),
            path(r'<slug:id>/stop/', self.stop_stream, name='streams_stream_stop'),
        ]
        return my_urls + urls

    def start_stream(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = Stream.objects.get(id=id)
        if not original.can_be_started:
            return redirect(reverse('admin:streams_stream_change', args=[original.id]))
        client = StreamsServiceClient()
        client.start_stream(original.id)
        return redirect(reverse('admin:streams_stream_change', args=[original.id]))

    def stop_stream(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = Stream.objects.get(id=id)
        if not original.can_be_stopped:
            return redirect(reverse('admin:streams_stream_change', args=[original.id]))
        client = StreamsServiceClient()
        client.stop_stream(original.id)
        return redirect(reverse('admin:streams_stream_change', args=[original.id]))

    def has_add_permission(self, request):
        return False
