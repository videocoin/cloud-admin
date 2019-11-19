from django.contrib import admin

from common.admin import DontLog
from .models import Transfer


@admin.register(Transfer)
class TransferAdmin(DontLog, admin.ModelAdmin):
    list_display = ('id', 'user_id', 'to_address', 'amount', 'kind', 'status')
    list_filter = ('kind', 'status')
    readonly_fields = ('id', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
