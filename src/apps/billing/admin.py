from django.conf import settings
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, resolve_url
from django.utils.html import format_html
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.http import HttpResponse, JsonResponse
from django.template import loader

from common.admin import DontLog, DeletedFilter
from .models import Account, Transaction


@admin.register(Account)
class AccountAdmin(DontLog, admin.ModelAdmin):

    list_display = (
        'id',
        'by',
        'email',
        'balance',
        'created_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def by(self, obj):
        if obj.user:
            url = resolve_url(admin_urlname(obj.user._meta, 'change'), obj.user.id)
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return ''
    by.short_description = 'user'
    by.allow_tags = True


@admin.register(Transaction)
class TransactionAdmin(DontLog, admin.ModelAdmin):
    list_display = ('id', 'from_account_link', 'to_account_link', 'created_at', 'amount', 'status', 'stream_link', 'profile_link')
    # list_display_links = ["from_account", "to_account"]

    list_filter = ('status', )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def from_account_link(self, obj):
        if obj.from_account:
            url = resolve_url(admin_urlname(obj.from_account._meta, 'change'), obj.from_account.id)
            return format_html('<a href="{}">{}</a>', url, obj.from_account.email)
        return ''
    from_account_link.short_description = 'from'
    from_account_link.allow_tags = True

    def to_account_link(self, obj):
        if obj.to_account:
            url = resolve_url(admin_urlname(obj.to_account._meta, 'change'), obj.to_account.id)
            return format_html('<a href="{}">{}</a>', url, obj.to_account.email)
        return ''
    to_account_link.short_description = 'from'
    to_account_link.allow_tags = True

    def stream_link(self, obj):
        if obj.stream:
            url = resolve_url(admin_urlname(obj.stream._meta, 'change'), obj.stream.id)
            return format_html('<a href="{}">{}</a>', url, obj.stream.name)
        return ''
    stream_link.short_description = 'stream'
    stream_link.allow_tags = True

    def profile_link(self, obj):
        if obj.profile:
            url = resolve_url(admin_urlname(obj.profile._meta, 'change'), obj.profile.id)
            return format_html('<a href="{}">{}</a>', url, obj.profile.name)
        return ''
    profile_link.short_description = 'profile'
    profile_link.allow_tags = True
