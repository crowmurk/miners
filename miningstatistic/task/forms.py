from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Config, ServerTask


class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = '__all__'
        exclude = ('slug', )

    def clean(self):
        cleaned_data = super().clean()

        # Если задано логирование в файл,
        # он должен быть указан
        if cleaned_data['log'] == self.Meta.model.FILE:
            if not cleaned_data['log_file']:
                self.add_error(
                    'log_file',
                    forms.ValidationError(
                        _("Log file is not specified"),
                        code='required',
                    ),
                )

        # Если отправляется статистика на Zabbix сервер,
        # должен быть указан его адрес и порт и таймаут
        if cleaned_data['zabbix_send']:
            if not cleaned_data['zabbix_server']:
                self.add_error(
                    'zabbix_server',
                    forms.ValidationError(
                        _("Zabbix server address is not specified"),
                        code='required',
                    ),
                )

            if not cleaned_data['zabbix_port']:
                self.add_error(
                    'zabbix_port',
                    forms.ValidationError(
                        _("Zabbix server port is not specified"),
                        code='required',
                    ),
                )

            if not cleaned_data['zabbix_timeout']:
                self.add_error(
                    'zabbix_timeout',
                    forms.ValidationError(
                        _("Timeout for Zabbix server is not specified"),
                        code='required',
                    ),
                )

        return cleaned_data


class ServerTaskForm(forms.ModelForm):
    class Meta:
        model = ServerTask
        fields = '__all__'
        exclude = ('executed', 'status')

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
                        _('%(miner)s miner does not support %(request)s'
                          ' request on %(server)s server'),
                        code='invalid',
                        params={
                            'server': server.name,
                            'miner': server.miner,
                            'request': request,
                        },
                    ),
                )

        return cleaned_data
