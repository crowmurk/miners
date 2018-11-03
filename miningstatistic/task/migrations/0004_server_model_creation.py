# Generated by Django 2.1.1 on 2018-09-25 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miner', '0007_miner_request_slug_unique_together'),
        ('task', '0003_enabled_config_ordering_first'),
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False)),
                ('last_executed', models.DateTimeField(null=True)),
                ('status', models.BooleanField(help_text='Результат последнего запуска', null=True)),
                ('requests', models.ManyToManyField(related_name='tasks', to='miner.Request')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='miner.Server')),
            ],
            options={
                'verbose_name': 'Опрос сервера',
                'ordering': ['server'],
            },
        ),
    ]
