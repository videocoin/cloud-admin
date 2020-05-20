import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.conf import settings

from .models import User, ApiToken, TestingUser
from streams.models import Stream
from miners.models import Miner
from accounts.models import Account
from common.admin import DontLog, HideDeletedInlineMixin


class TestingFilter(admin.SimpleListFilter):
    title = 'testing'
    parameter_name = 'testing'

    def lookups(self, request, model_admin):
        return (
            ('testing', 'testing'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'testing':
            return queryset.filter(testing_user__isnull=False)
        return queryset


class ApiTokensInlineAdmin(admin.TabularInline):
    model = ApiToken
    extra = 0
    readonly_fields = ('id', 'token', )
    fields = ('id', 'token', 'name', 'created_at')
    show_change_link = True


class StreamsInlineAdmin(HideDeletedInlineMixin, admin.TabularInline):
    model = Stream
    extra = 0
    fields = ('id', 'name', 'profile_id', 'status', 'input_status', 'stream_contract_id', 'created_at', 'updated_at')
    readonly_fields = ('id', 'name', 'profile_id', 'status', 'input_status', 'stream_contract_id', 'created_at', 'updated_at')
    show_change_link = True


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


class TestingUserInlineAdmin(admin.TabularInline):
    model = TestingUser
    extra = 0
    fields = ('delete_date',)
    can_delete = False


@admin.register(User)
class UserAdmin(DontLog, admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'role', 'address', 'is_active', 'is_testing', 'created_at')
    list_filter = ('role', 'is_active', TestingFilter, 'created_at')
    search_fields = ('id', 'email', 'name', 'apitoken__token__icontains')
    exclude = ('password', )
    readonly_fields = ['id', 'token', 'is_testing']
    ordering = ('-created_at',)
    change_form_template = 'admin/users/user_change_form.html'
    inlines = [TestingUserInlineAdmin, AccountsInlineAdmin, StreamsInlineAdmin, ApiTokensInlineAdmin, MinersInlineAdmin]

    fieldsets = (
        ('USER', {
            'fields': (
                'id',
                'email',
                'name',
                'role',
                'token',
                'created_at',
                'activated_at',
                'is_active',
            )
        }),
    )

    def is_testing(self, instance):
        return instance.is_testing
    is_testing.boolean = True

    def is_active(self, instance):
        return instance.is_active
    is_active.boolean = True

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/activate/', self.activate, name='users_user_activate'),
            path(r'<slug:id>/faucet/', self.faucet, name='users_user_faucet'),
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

    def faucet(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')
        original = User.objects.get(id=id)
        r = requests.post(
            settings.FAUCET_URL,
            json={"account": original.address, "amount": 10},
        )
        assert r.status_code == 200
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
