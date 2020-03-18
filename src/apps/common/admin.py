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
