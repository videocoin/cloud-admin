from django.contrib import admin

from .models import Miner


@admin.register(Miner)
class MinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')
    list_filter = ('status', )
