from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Config, Server

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = '__all__'
        exclude = ('slug', )

    def clean(self):
        cleaned_data = super().clean()

        # Если задано логирование в файл,
        # он должен быть указан
        if cleaned_data['log'] == self.Meta.model.FILE and not cleaned_data['log_file']:
            raise forms.ValidationError(
                {
                    'log_file': _("Не задан файл для ведения логов."),
                },
                code='required',
            )

        # Если отправляется статистика на Zabbix сервер,
        # он должен быть указан
        if cleaned_data['zabbix_send'] and not cleaned_data['zabbix_server']:
            raise forms.ValidationError(
                {
                    'zabbix_server': _("Не задан адрес Zabbix сервера."),
                },
                code='required',
            )

        return cleaned_data

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
        exclude = ('last_executed', 'status')

    def clean(self):
        cleaned_data = super().clean()

        # Заданные запросы должны соответствовать
        # установленному на сервере майнеру
        server = cleaned_data['server']
        for request in cleaned_data['requests']:
            if request.miner != server.miner:
                self.add_error(
                    'requests',
                    forms.ValidationError(
                        _('Запрос %(request)s не поддерживаются майнером'
                          ' %(miner)s на сервере %(server)s'),
                        code='invalid',
                        params={
                            'server': server.name,
                            'miner': server.miner,
                            'request': request,
                        },
                    ),
                )

        return cleaned_data
