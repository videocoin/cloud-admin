import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect

from .models import Task, Stream


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')
    list_filter = ('status', 'created_at',)
    change_form_template = 'admin/streams/task_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/stop/', self.stop, name='streams_task_stop'),
        ]
        return my_urls + urls

    def stop(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')

        original = Task.objects.get(id=id)
        domain = '{}://{}'.format(request.scheme, request.get_host())
        requests.post('{}/api/v1/streams/{}/stop"'.format(domain, original.id), headers={'Authorization': 'Bearer {}'.format(request.user.token)})
        return redirect(reverse('admin:streams_task_change', args=[original.id]))


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'input_status', 'refunded', 'created_at', 'ready_at', 'completed_at')
    list_filter = ('status', 'input_status', 'created_at', 'ready_at', 'completed_at')
    readonly_fields = ('id', 'stream_contract_address', 'created_at',  'updated_at', 'id', 'task_id', 'task_status',
                       'task_cmdline', 'task_input', 'task_output', 'task_render', )
    change_form_template = 'admin/streams/stream_change_form.html'

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
                'task_render',
            )
        }),
    )
