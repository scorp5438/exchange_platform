from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import AdForm
from .models import Ad, Category


class IndexView(ListView):
    template_name = 'ads/index.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = Ad.objects.select_related('category', 'user').all()

        category_id = self.request.GET.get('category')
        condition = self.request.GET.get('condition')
        search_query = self.request.GET.get('search')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if category_id and category_id.isdigit():
            category_id = int(category_id)
        else:
            category_id = 0

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset.order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['conditions'] = Ad.CONDITION
        context['search_query'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_condition'] = self.request.GET.get('condition', '')
        return context


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


class DeleteAdView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'ads/delete_ad.html'
    success_url = reverse_lazy('ads:index')

    def test_func(self):
        if self.request.user.is_superuser:
            return True

        created_by_current_user = self.get_object().user == self.request.user
        return created_by_current_user
