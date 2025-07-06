from django import forms
from django.core.exceptions import ValidationError

from .models import Ad, Category


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = 'title', 'description', 'image_url', 'category', 'condition',

    def clean_category(self):
        category = self.cleaned_data.get('category')

        if not Category.objects.filter(id=category.id).exists():
            raise ValidationError('Выберите существующую категорию')
        return category