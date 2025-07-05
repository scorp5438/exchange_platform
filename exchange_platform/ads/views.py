from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import  ListView, DetailView

from .models import Ad


class IndexView(ListView):
    queryset = Ad.objects.select_related('category', 'user').all()
    template_name = 'ads/index.html'

class DetailAdView(DetailView):
    queryset = Ad.objects.select_related('category', 'user').all()
    template_name = 'ads/detail.html'
