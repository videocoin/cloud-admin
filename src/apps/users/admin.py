import requests

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'role', 'balance')
    list_filter = ('role', 'is_active', 'created_at',)
    search_fields = ('email', 'name')
    exclude = ('password',)
    readonly_fields = ['id', 'token', 'balance']

    change_form_template = 'admin/users/user_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(r'<slug:id>/activate/', self.activate, name='users_user_activate'),
        ]
        return my_urls + urls

    def activate(self, request, id):
        if not request.user.is_superuser:
            raise PermissionError('you can\'t')

        original = User.objects.get(id=id)
        domain = '{}://{}'.format(request.scheme, request.get_host())
        requests.post('{}/api/v1/user/{}/activate'.format(domain, original.id), headers={'Authorization': 'Bearer {}'.format(request.user.token)})
        return redirect(reverse('admin:users_user_change', args=[original.id]))


from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

admin.site.unregister(Site)
admin.site.unregister(Group)

