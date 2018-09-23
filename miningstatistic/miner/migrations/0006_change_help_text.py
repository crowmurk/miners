# Generated by Django 2.1.1 on 2018-09-23 04:47

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miner', '0005_representation_and_validation_changes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='miner',
            name='slug',
            field=models.SlugField(editable=False, help_text='URL идентификатор объекта', max_length=63, unique=True, validators=[core.validators.ValidateSlug('Miner', ['name', 'version'])]),
        ),
        migrations.AlterField(
            model_name='request',
            name='response',
            field=models.TextField(blank=True, help_text='Шаблон проверки ответа', validators=[core.validators.validate_json]),
        ),
        migrations.AlterField(
            model_name='request',
            name='slug',
            field=models.SlugField(editable=False, help_text='URL идентификатор объекта', max_length=31, validators=[core.validators.ValidateSlug('Request', 'name')]),
        ),
        migrations.AlterField(
            model_name='server',
            name='slug',
            field=models.SlugField(editable=False, help_text='URL идентификатор объекта', max_length=31, unique=True, validators=[core.validators.ValidateSlug('Server', 'name')]),
        ),
    ]
