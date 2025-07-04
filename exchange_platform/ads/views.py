from django.views.generic import  ListView

from .models import Ad

class IndexView(ListView):
    queryset = Ad.objects.select_related('category', 'user').all()
    template_name = 'ads/index.html'
