# Generated by Django 2.1.1 on 2018-09-27 07:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_enabled_server_ordering_first'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='zabbix_port',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)]),
        ),
    ]