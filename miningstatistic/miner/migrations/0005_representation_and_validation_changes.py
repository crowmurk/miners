# Generated by Django 2.1.1 on 2018-09-22 21:45

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miner', '0004_request_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='miner',
            options={'ordering': ['name', 'version'], 'verbose_name': 'Майнер'},
        ),
        migrations.AlterModelOptions(
            name='request',
            options={'ordering': ['miner', 'name'], 'verbose_name': 'Запрос'},
        ),
        migrations.AlterModelOptions(
            name='server',
            options={'ordering': ['name'], 'verbose_name': 'Сервер'},
        ),
        migrations.AlterField(
            model_name='miner',
            name='slug',
            field=models.SlugField(editable=False, help_text='A label for URL config.', max_length=63, unique=True, validators=[core.validators.ValidateSlug('Miner', ['name', 'version'])]),
        ),
        migrations.AlterField(
            model_name='request',
            name='slug',
            field=models.SlugField(editable=False, help_text='A label for URL config.', max_length=31, validators=[core.validators.ValidateSlug('Request', 'name')]),
        ),
        migrations.AlterField(
            model_name='server',
            name='slug',
            field=models.SlugField(editable=False, help_text='A label for URL config.', max_length=31, unique=True, validators=[core.validators.ValidateSlug('Server', 'name')]),
        ),
    ]
