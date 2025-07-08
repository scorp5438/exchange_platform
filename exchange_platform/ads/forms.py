from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Ad,
    ExchangeProposal,
    Category
)


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = 'title', 'description', 'image_url', 'category', 'condition',

    def clean_category(self):
        category = self.cleaned_data.get('category')

        if not Category.objects.filter(id=category.id).exists():
            raise ValidationError('Выберите существующую категорию')
        return category


class BaseExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['comment', 'ad_sender']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            excluded_ids = self.get_excluded_ad_ids()

            self.fields['ad_sender'].queryset = Ad.objects.filter(
                user=self.user
            ).exclude(
                id__in=excluded_ids
            )

    def get_excluded_ad_ids(self):
        sent_ids = ExchangeProposal.objects.filter(
            status__in=['принята'],
            ad_sender__user=self.user
        ).values_list('ad_sender_id', flat=True)

        received_ids = ExchangeProposal.objects.filter(
            status__in=['принята'],
            ad_receiver__user=self.user
        ).values_list('ad_receiver_id', flat=True)

        return set(sent_ids) | set(received_ids)

    def clean_category(self):
        ad = self.cleaned_data.get('ad')

        if not Ad.objects.filter(ad_sender=ad).exists():
            raise ValidationError('Выберите существующее объявление')
        return ad


class CreateExchangeProposalForm(BaseExchangeProposalForm):
    class Meta(BaseExchangeProposalForm.Meta):
        pass


class SenderUpdateExchangeProposalForm(BaseExchangeProposalForm):
    class Meta(BaseExchangeProposalForm.Meta):
        fields = ['comment', 'ad_sender']


class ReceiverUpdateExchangeProposalForm(BaseExchangeProposalForm):
    class Meta(BaseExchangeProposalForm.Meta):
        fields = ['status']

