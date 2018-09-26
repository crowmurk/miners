from django import forms

from .models import Config, Server

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = '__all__'
        exclude = ('slug', )

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
        exclude = ('last_executed', 'status')
