import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.conf import settings

from .models import User, ApiToken
from transfers.models import Transfer
from streams.models import Stream
from miners.models import Miner
from accounts.models import Account


class ApiTokenInlineAdmin(admin.TabularInline):
    model = ApiToken
    extra = 0
    readonly_fields = ('id', 'token', )
    fields = ('id', 'token', 'name', 'created_at')
    show_change_link = True


class TransfersInlineAdmin(admin.TabularInline):
    model = Transfer
    extra = 0
    readonly_fields = ('id', 'pin', 'kind', 'status', 'to_address', 'amount', 'created_at', 'expires_at')
    fields = ('id', 'pin', 'kind', 'status', 'to_address', 'amount', 'created_at', 'expires_at')
    show_change_link = True


class StreamInlineAdmin(admin.TabularInline):
    model = Stream
    extra = 0
    fields = ('id', 'name', 'profile_id', 'status', 'input_status', 'stream_contract_id', 'created_at', 'updated_at')
    readonly_fields = ('id', 'name', 'profile_id', 'status', 'input_status', 'stream_contract_id', 'created_at', 'updated_at')
    show_change_link = True


class MinerInlineAdmin(admin.TabularInline):
    model = Miner
    extra = 0
    readonly_fields = ('id', 'last_ping_at', 'status', 'current_task_id', 'address', 'tags',  'system_info')
    fields = ('id', 'last_ping_at', 'status', 'current_task_id', 'address', 'tags',  'system_info')
    show_change_link = True


class AccountsInlineAdmin(admin.TabularInline):
    model = Account
    extra = 0
    readonly_fields = ('id', 'address', 'key', 'balance_wei', 'updated_at')
    fields = ('id', 'address', 'key', 'balance_wei', 'updated_at')
    show_change_link = True


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'role', 'balance_wei', 'address')
    list_filter = ('role', 'is_active', 'created_at',)
    search_fields = ('id', 'email', 'name')
    exclude = ('password',)
    readonly_fields = ['id', 'token', 'balance_wei', 'address']
    ordering = ('-created_at',)
    change_form_template = 'admin/users/user_change_form.html'
    inlines = [AccountsInlineAdmin, ApiTokenInlineAdmin, TransfersInlineAdmin, StreamInlineAdmin, MinerInlineAdmin]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        user_ids = list(ApiToken.objects.filter(token__icontains=search_term).values_list('user_id', flat=True))
        user_ids.extend(Transfer.objects.filter(id__icontains=search_term).values_list('user_id', flat=True))
        queryset = queryset.union(User.objects.filter(id__in=set(user_ids)))
        return queryset, use_distinct

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/activate/', self.activate, name='users_user_activate'),
            path(r'<slug:id>/faucet/', self.faucet, name='users_user_faucet'),
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
            json={"account": original.address, "amount": 100},
        )
        assert r.status_code == 200
        return redirect(reverse('admin:users_user_change', args=[original.id]))

@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'name', 'created_at')
    readonly_fields = ('id', 'token', 'user',)

    def has_add_permission(self, request):
        return False


from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

admin.site.unregister(Site)
admin.site.unregister(Group)

