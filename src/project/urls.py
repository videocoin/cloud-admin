from django.conf import settings
from django.views.static import serve
from django.conf.urls import url
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path

admin.autodiscover()
admin.site.site_header = 'Videocoin Administration'


def health(request):
    return HttpResponse('OK')


urlpatterns = [
    url(r'^healthz', health, name='health'),
    path('imsgx72bs1pxd72mxs/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += [
        url(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': settings.STATIC_ROOT}
        ),
        url(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT}
        ),
    ]
