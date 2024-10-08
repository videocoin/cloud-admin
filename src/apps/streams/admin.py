from django.conf import settings
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, resolve_url
from django.utils.html import format_html
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.http import HttpResponse, JsonResponse
from django.template import loader

from common.admin import DontLog, DeletedFilter
from videocoin.blockchain import Blockchain
from videocoin.validators import ValidatorCollection
from .models import Stream, Task, TaskTransaction


class TaskTransactionInlineAdmin(admin.TabularInline):
    model = TaskTransaction
    extra = 0
    show_change_link = False
    show_delete_link = False
    readonly_fields = (
        'id', 'created_at', 'stream_contract_id', 'stream_contract_address', 'add_input_chunk_tx',
        'add_input_chunk_tx_status', 'submit_proof_tx',  'submit_proof_tx_status', 'validate_proof_tx', 'validate_proof_tx_status',
        'scrap_proof_tx', 'scrap_proof_tx_status',
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TasksInlineAdmin(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('id_link', 'status', 'cmdline', 'uri', 'is_live', 'is_lock', 'path', 'client_id', 'machine_type')
    readonly_fields = ('id_link', 'status', 'cmdline', 'uri', 'is_live', 'is_lock', 'path', 'client_id', 'machine_type')
    show_change_link = False
    show_delete_link = False

    def id_link(self, obj):
        url = resolve_url(admin_urlname(obj._meta, 'change'), obj.id)
        return format_html('<a href="{}">{}</a>', url, obj.id)
    id_link.short_description = 'Id'
    id_link.allow_tags = True

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Stream)
class StreamAdmin(DontLog, admin.ModelAdmin):
    inlines = [TasksInlineAdmin]

    list_display = (
        'id',
        'name',
        'owned_by',
        'profile_set',
        'status',
        'input_status',
        'total_cost',
        'get_input_url',
        'get_output_url',
        'input_type',
        'output_type',
        'created_at',
        'ready_at',
        'completed_at',
    )

    list_filter = (
        DeletedFilter,
        'status',
        'input_status',
        'input_type',
        'output_type',
        'created_at',
        'ready_at',
        'completed_at',
    )

    readonly_fields = (
        'id',
        'profile_set',
        'refunded',
        'stream_contract_id',
        'stream_contract_address',
        'get_input_url',
        'get_output_url',
        'get_rtmp_url',
        'created_at',
        'ready_at',
        'updated_at',
        'completed_at',
        'deleted_at',
        'owned_by',
        'validation_field',
        'input_type',
        'total_cost',
    )

    change_form_template = 'admin/streams/stream_change_form.html'
    search_fields = ('id', 'name', 'by__email')

    def validation_field(self, obj):
        url_validate = reverse('admin:streams_stream_validate', args=[obj.id])
        url_events = reverse('admin:streams_stream_events', args=[obj.id])
        html = '''<button type="button" class="validate btn btn-info" data-url={} style="display: inline-block;
                background: #609ab6;
                border-radius: 4px;
                padding: 10px 15px;
                line-height: 15px;
                text-align: left;
                color: #fff;">validate</button>'''.format(url_validate)
        if obj.stream_contract_address:
            html += '''<a href="{}" style="padding: 10px 15px;">Blockchain events</a>'''.format(url_events)
        html += '<div class="validate_result"><img src="https://i.giphy.com/l3nWhI38IWDofyDrW.gif" class="validate_loading" style="display:none; width:200px;"/ ></div>'
        return format_html(html)

    validation_field.short_description = "Actions"
    validation_field.allow_tags = True

    fieldsets = (
        ('Stream', {
            'fields': (
                'id',
                'name',
                'status',
                'input_status',
                'total_cost',
                'input_type',
                'output_type',
                'profile_set',
                'stream_contract_id',
                'stream_contract_address',
                'owned_by',
                'drm_xml',
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
                'deleted_at',
            )
        }),
        ('Blockchain', {
            'fields': (
                'validation_field',
            )
        }),
    )

    class Media:
        css = {
            'all': ('admin.css', )
        }
        js = ['admin.js']

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
         return format_html('<a target="_blank" href="{}" />{}</a>', obj.rtmp_url, obj.rtmp_url)
    get_rtmp_url.short_description = "RTMP"

    def get_input_url(self, obj):
         return format_html('<a target="_blank" href="{}" />{}</a>', obj.input_url, obj.input_url)
    get_input_url.short_description = "Input"

    def get_output_url(self, obj):
         return format_html('<a target="_blank" href="{}" />{}</a>', obj.output_url, obj.output_url)
    get_output_url.short_description = "Output"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/start/', self.start_stream, name='streams_stream_start'),
            path(r'<slug:id>/stop/', self.stop_stream, name='streams_stream_stop'),
            path(r'<slug:id>/events/', self.admin_site.admin_view(self.events), name='streams_stream_events'),
            path(r'<slug:id>/validate/', self.validate, name='streams_stream_validate'),
        ]
        return my_urls + urls

    def start_stream(self, request, id):
        from github.com.videocoin.cloud_api.streams.private.v1.client import StreamsServiceClient
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = Stream.objects.get(id=id)
        if not original.can_be_started:
            return redirect(reverse('admin:streams_stream_change', args=[original.id]))
        client = StreamsServiceClient()
        client.start_stream(original.id)
        return redirect(reverse('admin:streams_stream_change', args=[original.id]))

    def stop_stream(self, request, id):
        from github.com.videocoin.cloud_api.streams.private.v1.client import StreamsServiceClient
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = Stream.objects.get(id=id)
        if not original.can_be_stopped:
            return redirect(reverse('admin:streams_stream_change', args=[original.id]))
        client = StreamsServiceClient()
        client.stop_stream(original.id)
        return redirect(reverse('admin:streams_stream_change', args=[original.id]))

    def events(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        stream = Stream.objects.get(id=id)

        context = {
            'original': stream,
            'opts': Stream._meta,
            'change': True,
            'has_delete_permission': False,
            'has_add_permission': False,
            'has_change_permission': False,
            'has_view_permission': True,
            'add': False,
        }

        blockchain = Blockchain(
            settings.SYMPHONY_KEY,
            settings.SYMPHONY_ADDR,
            settings.SYMPHONY_OAUTH2_CLIENTID,
            stream_id=stream.stream_contract_id,
            stream_address=stream.stream_contract_address,
            stream_manager_address=settings.STREAM_MANAGER_CONTRACT_ADDR
        )

        if not blockchain.is_connected():
            context.update({
                'error': 'Can not connect to blockchain...'
            })

        events = blockchain.get_all_events()
        events = sorted(events, key=lambda e: e['blockInfo']['timestamp'])

        context.update({
            'events': events,
            'tasks': stream.tasks.all(),
        })
        template = loader.get_template('admin/streams/events.html')

        return HttpResponse(template.render(context, request))

    def validate(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        stream = Stream.objects.get(id=id)

        blockchain = Blockchain(
            settings.SYMPHONY_KEY,
            settings.SYMPHONY_ADDR,
            settings.SYMPHONY_OAUTH2_CLIENTID,
            stream_id=stream.stream_contract_id,
            stream_address=stream.stream_contract_address,
            stream_manager_address=settings.STREAM_MANAGER_CONTRACT_ADDR
        )

        if not blockchain.is_connected():
            return JsonResponse({'error': 'Can not connect to blockchain...'}, status=400)

        events = blockchain.get_all_events()
        validator = ValidatorCollection(
            events=events,
            input_url=stream.input_url,
            output_url=stream.output_url
        )
        return JsonResponse(validator.validate(), status=200)

    def has_add_permission(self, request):
        return False


@admin.register(Task)
class TasksAdmin(DontLog, admin.ModelAdmin):
    model = Task
    inlines = [TaskTransactionInlineAdmin]
    list_display = ('id', 'status', 'is_lock', 'is_live', 'uri', 'path', 'client_id', 'machine_type')
    list_filter = ('status', )
    readonly_fields = ('id', 'uri', 'is_live', 'path', 'client_id', 'machine_type')
