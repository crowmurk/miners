from django import forms
from django.forms.widgets import HiddenInput

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
        exclude = ('slug', )
        widgets = {'miner': HiddenInput()}


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
        exclude = ('slug', )
