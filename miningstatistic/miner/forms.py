from django import forms
from django.core.exceptions import ValidationError

from .models import Miner, Request, Server


class MinerForm(forms.ModelForm):
    class Meta:
        model = Miner
        fields = '__all__'
        exclude = ('slug', )


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'

        exclude = ('miner', 'slug')

    def clean(self):
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        miner_obj = self.data.get('miner')
        exists = (
            Request.objects.filter(
                slug__iexact=slug,
                miner=miner_obj,
            ).exists())
        if exists:
            raise ValidationError(
                "Request с таким slug "
                "и miner уже существует.")
        else:
            return cleaned_data

    def save(self, **kwargs):
        instance = super().save(commit=False)
        instance.miner = (self.data.get('miner'))
        instance.save()
        self.save_m2m()
        return instance


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
        exclude = ('slug', )
