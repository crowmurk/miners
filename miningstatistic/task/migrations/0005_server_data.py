# Generated by Django 2.1.1 on 2018-09-26 07:00

from django.db import migrations

SERVERS = [
    {
        'server': 'r11',
        'requests': ['statistic', ],
    },
    {
        'server': 'r12',
        'requests': ['statistic', ],
    },
    {
        'server': 'r13',
        'requests': ['statistic', ],
    },
    {
        'server': 'r14',
        'requests': ['statistic', ],
    },
    {
        'server': 'r15',
        'requests': ['statistic', ],
    },
    {
        'server': 'r16',
        'requests': ['statistic', ],
    },
    {
        'server': 'r17',
        'requests': ['statistic', ],
    },
    {
        'server': 'r18',
        'requests': ['statistic', ],
    },
    {
        'server': 'r19',
        'requests': ['statistic', ],
    },
    {
        'server': 'r21',
        'requests': ['summary', 'stats', ],
    },
    {
        'server': 'r23',
        'requests': ['summary', 'stats', ],
    },
    {
        'server': 'r24',
        'requests': ['summary', 'stats', ],
    },
    {
        'server': 'r25',
        'requests': ['summary', 'stats', ],
    },
    {
        'server': 'r27',
        'requests': ['summary', 'stats', ],
    },
    {
        'server': 'r28',
        'requests': ['summary', 'stats', ],
    },
    {
        'server': 'r29',
        'requests': ['summary', 'stats', ],
    },
]

def add_server_data(apps, schema_editor):
    TaskServer = apps.get_model('task', 'Server')
    MinerServer = apps.get_model('miner', 'Server')
    MinerRequest = apps.get_model('miner', 'Request')
    for server in SERVERS:
        miner_server = MinerServer.objects.get(
            slug=server['server'],
        )
        requests = MinerRequest.objects.filter(
            miner=miner_server.miner,
            slug__in=server['requests'],
        )
        new_server = TaskServer.objects.create(
            server=miner_server,
            enabled=True,
        )
        new_server.requests.set(requests)
        new_server.save()

def remove_server_data(apps, schema_editor):
    TaskServer = apps.get_model('task', 'Server')
    for server in SERVERS:
        deleted_servers = TaskServer.objects.filter(
            server__slug=server['server'],
        )
        for slug in server['requests']:
            deleted_servers = deleted_servers.filter(
                requests__slug=slug,
            )
        deleted_servers.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_server_model_creation'),
    ]

    operations = [
        migrations.RunPython(
            add_server_data,
            remove_server_data)
    ]
