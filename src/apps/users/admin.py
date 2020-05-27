import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect

from .models import User, ApiToken
from streams.models import Stream
from miners.models import Miner
from accounts.models import Account
from common.admin import DontLog, HideDeletedInlineMixin


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


@admin.register(ApiToken)
class ApiTokenAdmin(DontLog, admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'name', 'created_at')
    readonly_fields = ('id', 'token', 'user',)

    def has_add_permission(self, request):
        return False
