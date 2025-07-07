from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import AdForm, CreateExchangeProposalForm, SenderUpdateExchangeProposalForm, \
    ReceiverUpdateExchangeProposalForm
from .models import Ad, ExchangeProposal, Category


class IndexView(ListView):
    template_name = 'ads/index.html'
    paginate_by = 6

    def get_queryset(self):
        sent_ids = ExchangeProposal.objects.filter(
            status__in=['принята'],
        ).values_list('ad_sender_id', flat=True)

        received_ids = ExchangeProposal.objects.filter(
            status__in=['принята'],
        ).values_list('ad_receiver_id', flat=True)

        excluded_ids = set(sent_ids) | set(received_ids)

        queryset = Ad.objects.select_related(
            'category',
            'user'
        ).exclude(
            id__in=excluded_ids
        )

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
    success_url = reverse_lazy('ads:index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateAdView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    template_name = 'ads/update_ad.html'
    form_class = AdForm

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


class ExcPropsView(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = 'ads/exc_props.html'

    def get_queryset(self):
        user = self.request.user
        queryset = ExchangeProposal.objects.select_related(
            'ad_sender',
            'ad_receiver',
            'ad_sender__user',
            'ad_receiver__user'
        ).filter(
            Q(ad_sender__user=user) | Q(ad_receiver__user=user)
        )

        status = self.request.GET.get('status')

        if status:
            queryset = queryset.filter(status=status)

        proposal_type = self.request.GET.get('type')
        if proposal_type == 'sent':
            queryset = queryset.filter(ad_sender__user=user)
        elif proposal_type == 'received':
            queryset = queryset.filter(ad_receiver__user=user)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Добавляем статистику для фильтров
        context.update({
            'status': ExchangeProposal.STATUSES,
            'current_status': self.request.GET.get('status', ''),
            'current_type': self.request.GET.get('type', ''),
            'sent_count': ExchangeProposal.objects.filter(ad_sender__user=user).count(),
            'received_count': ExchangeProposal.objects.filter(ad_receiver__user=user).count(),
        })
        return context


class CreateExcPropsView(LoginRequiredMixin, CreateView):
    model = ExchangeProposal
    template_name = 'ads/create_exc_props.html'
    form_class = CreateExchangeProposalForm

    def get_success_url(self):
        return reverse('ads:detail_ad', kwargs={'pk': self.object.ad_receiver.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_receiver'] = Ad.objects.filter(id=self.kwargs.get('pk')).first()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.ad_receiver = Ad.objects.get(id=self.kwargs.get('pk'))
        return super().form_valid(form)


class DetailExcPropView(DetailView):
    queryset = ExchangeProposal.objects.select_related(
        'ad_sender',
        'ad_receiver',
        'ad_sender__user',
        'ad_receiver__user'
    )
    template_name = 'ads/detail_exc_props.html'


class UpdateExcPropsView(UpdateView):
    model = ExchangeProposal
    template_name = 'ads/update_exc_props.html'

    def get_success_url(self):
        return reverse('ads:detail_exc_props', kwargs={'pk': self.object.pk})

    def test_func(self):
        created_by_current_user = self.get_object().ad_sender.user == self.request.user
        return created_by_current_user

    def get_form_class(self):
        proposal = self.get_object()

        if proposal.ad_sender.user == self.request.user:
            return SenderUpdateExchangeProposalForm
        elif proposal.ad_receiver.user == self.request.user:
            return ReceiverUpdateExchangeProposalForm
        else:
            raise PermissionDenied("У вас нет прав для редактирования этого предложения.")
