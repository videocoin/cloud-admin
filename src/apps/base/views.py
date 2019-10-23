from django.views.generic.base import TemplateView, View


class HomeView(TemplateView):
    template_name = 'index.html'
