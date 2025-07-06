from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .models import Ad
from .forms import AdForm

class IndexView(ListView):
    queryset = Ad.objects.select_related('category', 'user').all()
    template_name = 'ads/index.html'

class DetailAdView(DetailView):
    queryset = Ad.objects.select_related('category', 'user').all()
    template_name = 'ads/detail.html'


class CreateAdView(LoginRequiredMixin, CreateView):
    model = Ad
    template_name = 'ads/create_ad.html'
    form_class = AdForm
    # fields = 'title', 'description', 'image_url', 'category', 'condition',
    success_url = reverse_lazy('ads:index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateAdView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    template_name = 'ads/update_ad.html'
    form_class = AdForm
    # fields = 'title', 'description', 'image_url', 'category', 'condition'
    # success_url = reverse_lazy('ads:detail_ad')

    def get_success_url(self):
        return reverse('ads:detail_ad', kwargs={'pk': self.object.pk})

    def test_func(self):
        if self.request.user.is_superuser:
            return True

        created_by_current_user = self.get_object().user == self.request.user
        return created_by_current_user
