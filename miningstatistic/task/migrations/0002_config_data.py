# Generated by Django 2.1.1 on 2018-09-24 19:40

from django.db import migrations

from core.utils import get_unique_slug

CONFIGS = [
    {
        "name": "Default",
        "zabbix_server": "192.168.1.4",
        "zabbix_send": True,
        "enabled": False,
        "log": "SY",
        "description": "Рабочая конфигурация"
    },
    {
        "name": "Develop",
        "zabbix_server": "",
        "zabbix_send": False,
        "enabled": True,
        "log": "ST",
        "description": "Конфигурация для отладки"
    },
]

def add_config_data(apps, schema_editor):
    Config = apps.get_model('task', 'Config')
    for config in CONFIGS:
        new_config = Config(
            name=config['name'],
            zabbix_server=config['zabbix_server'],
            zabbix_send=config['zabbix_send'],
            enabled=config['enabled'],
            log=config['log'],
            description=config['description'],
        )
        new_config.slug = get_unique_slug(
            new_config,
            'slug',
            'name',
        )
        new_config.save()


def remove_config_data(apps, schema_editor):
    Config = apps.get_model('task', 'Config')
    for config in CONFIGS:
        config_object = Config.objects.get(
            name=config['name'],
        )
        config_object.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_config_data,
            remove_config_data)
    ]