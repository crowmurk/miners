# Generated by Django 2.1.1 on 2018-09-24 19:40

import core.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, unique=True)),
                ('slug', models.SlugField(editable=False, help_text='URL идентификатор объекта', max_length=63, unique=True, validators=[core.validators.validate_slug])),
                ('enabled', models.BooleanField(default=False)),
                ('refresh', models.PositiveSmallIntegerField(default=30, help_text='Интервал опроса серверов (сек.).', validators=[django.core.validators.MinValueValidator(10)])),
                ('zabbix_server', models.GenericIPAddressField(blank=True, null=True, validators=[django.core.validators.validate_ipv46_address])),
                ('zabbix_port', models.PositiveIntegerField(default=10051, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)])),
                ('zabbix_send', models.BooleanField(default=False, help_text='Отправлять статистику Zabbix серверу.')),
                ('log', models.CharField(choices=[('NO', 'Выключить'), ('SY', 'Системный журнал'), ('ST', 'Консоль'), ('FI', 'Файл')], default='SY', max_length=2)),
                ('log_file', models.FilePathField(blank=True)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'Конфигурация',
                'ordering': ['name'],
            },
        ),
    ]