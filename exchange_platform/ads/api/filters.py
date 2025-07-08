from django_filters import rest_framework as filters
from ..models import ExchangeProposal

class ExchangeProposalFilter(filters.FilterSet):
    ad_sender = filters.CharFilter(  # Изменил имя поля для удобства
        field_name='ad_sender__user__username',
        lookup_expr='iexact',
        label='Имя отправителя'
    )
    ad_receiver = filters.CharFilter(
        field_name='ad_receiver__user__username',
        lookup_expr='iexact',
        label='Имя получателя'
    )

    class Meta:
        model = ExchangeProposal
        fields = ['status', 'ad_sender', 'ad_receiver']