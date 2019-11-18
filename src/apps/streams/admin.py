import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect

from .models import Stream


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'user', 'input_status', 'refunded', 'created_at', 'ready_at', 'completed_at')
    list_filter = ('status', 'input_status', 'created_at', 'ready_at', 'completed_at')
    readonly_fields = ('id', 'stream_contract_address', 'created_at',  'updated_at', 'id', 'task_id', 'task_status',
                       'task_cmdline', 'task_input', 'task_output', 'task_client_id')
    change_form_template = 'admin/streams/stream_change_form.html'
    search_fields = ('id', 'name')

    fieldsets = (
        ('Stream', {
            'fields': (
                'id',
                'name',
                'status',
                'input_status',
                'profile_id',
                'stream_contract_id',
                'stream_contract_address',
                'refunded',

            )
        }),
        ('Stream urls', {
            'fields': (
                'input_url',
                'output_url',
                'rtmp_url',
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

        return redirect(reverse('admin:streams_stream_change', args=[original.id]))

    def stop_stream(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = Stream.objects.get(id=id)
        if not original.can_be_stopped:
            return redirect(reverse('admin:streams_stream_change', args=[original.id]))

        return redirect(reverse('admin:streams_stream_change', args=[original.id]))

    def has_add_permission(self, request):
        return False
