from django import forms

from .models import ServerStatistic


class ServerStatisticForm(forms.ModelForm):
    class Meta:
        model = ServerStatistic
        fields = '__all__'
