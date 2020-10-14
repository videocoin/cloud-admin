import csv
from collections import defaultdict
from functools import update_wrapper

import requests
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse

from accounts.models import Account
from billing.models import Transaction
from common.admin import DontLog, HideDeletedInlineMixin
from miners.models import Miner
from streams.models import Stream
from .models import User, ApiToken, UserReportProxy


class ApiTokensInlineAdmin(admin.TabularInline):
    model = ApiToken
    extra = 0
    readonly_fields = ('id', 'token', )
    fields = ('id', 'token', 'name', 'created_at')
    show_change_link = True


class StreamsInlineAdmin(HideDeletedInlineMixin, admin.TabularInline):
    model = Stream
    extra = 0
    fields = ('id', 'name', 'profile_id', 'status', 'input_status', 'stream_contract_id', 'created_at', 'updated_at', 'total_cost')
    readonly_fields = ('id', 'name', 'profile_id', 'status', 'input_status', 'stream_contract_id', 'created_at', 'updated_at', 'total_cost')
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False


class MinersInlineAdmin(HideDeletedInlineMixin, admin.TabularInline):
    model = Miner
    extra = 0
    readonly_fields = ('id', 'last_ping_at', 'status', 'current_task_id', 'address', 'tags',  'system_info')
    fields = ('id', 'last_ping_at', 'status', 'current_task_id', 'address', 'tags',  'system_info')
    show_change_link = True


class AccountsInlineAdmin(admin.TabularInline):
    model = Account
    extra = 0
    readonly_fields = ('id', 'address', 'key', 'updated_at')
    fields = ('id', 'address', 'key', 'updated_at')
    show_change_link = True


@admin.register(User)
class UserAdmin(DontLog, admin.ModelAdmin):
    list_display = ('id', 'email', 'display_name', 'uirole', 'role', 'address', 'is_active', 'created_at')
    list_filter = ('role', 'uirole', 'is_active', 'country', 'created_at')
    search_fields = ('id', 'email', 'first_name', 'last_name', 'apitoken__token__icontains')
    exclude = ('password', )
    readonly_fields = ['id', 'token',  'display_name', 'name']
    ordering = ('-created_at',)
    change_form_template = 'admin/users/user_change_form.html'
    inlines = [AccountsInlineAdmin, StreamsInlineAdmin, ApiTokensInlineAdmin, MinersInlineAdmin]

    fieldsets = (
        ('USER', {
            'fields': (
                'id',
                'email',
                'name',
                'first_name',
                'last_name',
                'role',
                'uirole',
                'token',
                'created_at',
                'activated_at',
                'is_active',
            )
        }),
        ('ADDRESS', {
            'fields': (
                'country',
                'region',
                'city',
                'zip',
                'address_1',
                'address_2',
            )
        }),
    )

    def is_active(self, instance):
        return instance.is_active
    is_active.boolean = True

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/activate/', self.activate, name='users_user_activate'),
            path(r'<slug:id>/block/', self.block, name='users_user_block'),
            path(r'<slug:id>/unblock/', self.unblock, name='users_user_unblock'),
        ]
        return my_urls + urls

    def activate(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')

        original = User.objects.get(id=id)
        domain = '{}://{}'.format(request.scheme, request.get_host())
        requests.post('{}/api/v1/user/{}/activate'.format(domain, original.id), headers={'Authorization': 'Bearer {}'.format(request.user.token)})
        return redirect(reverse('admin:users_user_change', args=[original.id]))

    def block(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = User.objects.get(id=id)
        original.is_active = False
        original.save(update_fields=['is_active'])
        return redirect(reverse('admin:users_user_change', args=[original.id]))

    def unblock(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = User.objects.get(id=id)
        original.is_active = True
        original.save(update_fields=['is_active'])
        return redirect(reverse('admin:users_user_change', args=[original.id]))


# @admin.register(ApiToken)
class ApiTokenAdmin(DontLog, admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'name', 'created_at')
    readonly_fields = ('id', 'token', 'user',)

    def has_add_permission(self, request):
        return False


@admin.register(UserReportProxy)
class UserReportAdmin(DontLog, admin.ModelAdmin):
    revert_url = '/admin/events/userreport/'
    model_name = 'userreport'
    loaded_usd_cache = defaultdict(int)
    spent_cache = defaultdict(int)

    list_display = (
        'email', 'display_name', 'streams_count', 'loaded_usd', 'spent',
        'created_at')
    readonly_fields = (
        'email', 'display_name', 'streams_count', 'loaded_usd', 'spent',
        'created_at')

    change_list_template = 'admin/users/userreport_change_list.html'

    def get_queryset(self, request):
        self.loaded_usd_cache = defaultdict(int)
        self.spent_cache = defaultdict(int)

        qs = super().get_queryset(request)
        qs = qs.annotate(streams_count=Count('stream', distinct=True))

        txs = Transaction.objects\
            .filter(status="SUCCESS")\
            .select_related('from_account', 'to_account')
        for tx in txs:
            if tx.from_account.email == "bank@videocoin.net":
                self.loaded_usd_cache[tx.to_account.email] += tx.amount
            self.spent_cache[tx.from_account.email] += tx.amount

        return qs

    def streams_count(self, obj):
        return obj.streams_count

    streams_count.short_description = 'Streams count'
    streams_count.allow_tags = True
    streams_count.admin_order_field = 'streams_count'

    def loaded_usd(self, obj):
        return int(self.loaded_usd_cache[obj.email] / 100)

    loaded_usd.short_description = 'Loaded USD'
    loaded_usd.allow_tags = True
    loaded_usd.admin_order_field = 'loaded_usd'

    def spent(self, obj):
        return round(float(self.spent_cache[obj.email]) / 100, 2)

    spent.short_description = 'Spent'
    spent.allow_tags = True
    spent.admin_order_field = 'spent'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()

        info = self.model._meta.app_label, self.model._meta.model_name

        custom_urls = [
            path(
                'download/',
                wrap(self.download_view),
                name='%s_%s_download' % info),
        ]
        return custom_urls + urls

    def download_view(self, request):
        qs = self.get_queryset(request)

        if not request.user or not request.user.is_staff:
            return HttpResponse()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user-report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'email', 'name', 'streams_count', 'loaded_usd', 'spent',
            'created_at'])
        for item in qs:
            writer.writerow([
                item.email, item.display_name, item.streams_count,
                self.loaded_usd(item), self.spent(item), item.created_at])

        return response
