from django.contrib import admin
from django import forms

from prettyjson import PrettyJSONWidget

from .models import Profile
from common.admin import DontLog


class ProfileForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = '__all__'
    widgets = {
      'spec': PrettyJSONWidget(attrs={'initial': 'parsed'}),
    }


@admin.register(Profile)
class ProfileAdmin(DontLog, admin.ModelAdmin):

    form = ProfileForm

    list_display = (
      'name',
      'id',
      'is_enabled',
      'reward',
      'deposit',
    )

    list_filter = ('is_enabled', )

    readonly_fields = (
      'id',
      'render',
    )

    fieldsets = (
        ('Profile', {
            'fields': (
                'id',
                'name',
                'description',
                'is_enabled',
                'spec',
                'render',
                'reward',
                'deposit',
            )
        }),
    )

