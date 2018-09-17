from django import forms
from django.core.exceptions import ValidationError

from .models import Miner, Request, Server


class SlugCleanMixin:
    """Вспомогательный класс для проверки поля slug."""
    def clean_slug(self):
        new_slug = (self.cleaned_data['slug'].lower())
        if new_slug == 'create':
            raise ValidationError('Slug may not be ""create".')
        return new_slug


class MinerForm(SlugCleanMixin, forms.ModelForm):
    class Meta:
        model = Miner
        fields = '__all__'


class RequestForm(SlugCleanMixin, forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'


class ServerForm(SlugCleanMixin, forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
