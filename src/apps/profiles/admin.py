from django.contrib import admin
from django import forms

from .models import Profile

from prettyjson import PrettyJSONWidget


class JsonForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = '__all__'
    widgets = {
      'spec': PrettyJSONWidget(),
    }


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = JsonForm
    list_display = ('id', 'name', 'is_enabled')
    list_filter = ('is_enabled', )
    readonly_fields = ('id', 'render', )

    fieldsets = (
        ('Profile', {
            'fields': (
                'id',
                'name',
                'description',
                'is_enabled',
                'spec',
                'render',
            )
        }),
    )

