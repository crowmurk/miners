from django import forms

from .models import Miner, Request, Server


class MinerForm(forms.ModelForm):
    class Meta:
        model = Miner
        fields = '__all__'


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
