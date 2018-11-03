# Generated by Django 2.1.1 on 2018-09-17 18:46

from django.db import migrations

from core.utils import get_unique_slug


MINERS = [
    {
        "name": "Claymore's Dual Ethereum",
        "version": "AMD GPU 9.8",
        "description": "",
    },
    {
        "name": "Claymore's CryptoNote",
        "version": "GPU 9.7",
        "description": "",
    },
    {
        "name": "EWBF's CUDA ZCash",
        "version": "0.3.4b",
        "description": "",
    },
    {
        "name": "Antminer S9 CGMiner",
        "version": "4.9.0",
        "description": "",
    },
]

def add_miner_data(apps, schema_editor):
    Miner = apps.get_model('miner', 'Miner')
    for miner in MINERS:
        new_miner = Miner(
            name=miner['name'],
            version=miner['version'],
            description=miner['description'],
        )
        new_miner.slug = get_unique_slug(
            new_miner,
            'slug',
            'name', 'version',
        )
        new_miner.save()


def remove_miner_data(apps, schema_editor):
    Miner = apps.get_model('miner', 'Miner')
    for miner in MINERS:
        miner_object = Miner.objects.get(
            name=miner['name'],
            version=miner['version'],
        )
        miner_object.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('miner', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_miner_data,
            remove_miner_data)
    ]