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
        if cleaned_data['log'] == self.Meta.model.FILE:
            if not cleaned_data['log_file']:
                self.add_error(
                    'log_file',
                    forms.ValidationError(
                        _("Не задан файл для ведения логов."),
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
                        _("Не задан адрес Zabbix сервера."),
                        code='required',
                    ),
                )

            if not cleaned_data['zabbix_port']:
                self.add_error(
                    'zabbix_port',
                    forms.ValidationError(
                        _("Не задан порт Zabbix сервера."),
                        code='required',
                    ),
                )

            if not cleaned_data['zabbix_timeout']:
                self.add_error(
                    'zabbix_timeout',
                    forms.ValidationError(
                        _("Не задан таймаут Zabbix сервера."),
                        code='required',
                    ),
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
