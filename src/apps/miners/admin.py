from django.contrib import admin

from .models import Miner


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')
    list_filter = ('status', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
