from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

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


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['comment', 'ad_sender']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            sent_ids = ExchangeProposal.objects.filter(
                status__in=['ожидает', 'принята'],
                ad_sender__user=self.user
            ).values_list('ad_sender_id', flat=True)

            received_ids = ExchangeProposal.objects.filter(
                status__in=['ожидает', 'принята'],
                ad_receiver__user=self.user
            ).values_list('ad_receiver_id', flat=True)

            excluded_ids = set(sent_ids) | set(received_ids)

            self.fields['ad_sender'].queryset = Ad.objects.filter(
                user=self.user
            ).exclude(
                id__in=excluded_ids
            )

    def clean_category(self):
        ad = self.cleaned_data.get('ad')

        if not Ad.objects.filter(ad_sender=ad).exists():
            raise ValidationError('Выберите существующее объявление')
        return ad
