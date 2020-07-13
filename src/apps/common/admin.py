from django.contrib import admin


class DontLog:

    def log_addition(self, *args):
        return

    def log_change(self, *args):
        return

    def log_deletion(self, *args):
        return


class DeletedFilter(admin.SimpleListFilter):
    title = 'deleted'
    parameter_name = 'deleted'

    def lookups(self, request, model_admin):
        return (
            ('deleted', 'deleted'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset.filter(deleted_at__isnull=True)
        if value == 'deleted':
            return queryset.filter(deleted_at__isnull=False)
        return queryset


class HideDeletedInlineMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(deleted_at__isnull=True)


from django.contrib.auth.models import Group

admin.site.unregister(Group)


from django.contrib.admin.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(DontLog, admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_repr', 'action_flag', 'action_time')
    list_filter = ('content_type', 'action_flag', 'action_time')

    search_fields = ('user__email__icontains', )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
