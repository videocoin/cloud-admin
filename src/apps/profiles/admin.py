from django.contrib import admin
from django import forms

from prettyjson import PrettyJSONWidget

from .models import Profile
from common.admin import DontLog


class JsonForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = '__all__'
    widgets = {
      'spec': PrettyJSONWidget(),
    }


@admin.register(Profile)
class ProfileAdmin(DontLog, admin.ModelAdmin):
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

