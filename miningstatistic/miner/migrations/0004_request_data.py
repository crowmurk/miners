# Generated by Django 2.1.1 on 2018-09-18 11:57

import json

from django.db import migrations

from core.utils import get_unique_slug


REQUESTS = [
    {
        'name': 'Statistic',
        'request': '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}',
        'response': json.dumps(
            {
                'Statistic': {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "error": {"type": "null"},
                        "result": {
                            "items": {"type": "string"},
                            "minItems": 9,
                            "maxItems": 9,
                        },
                    },
                },
            },
        ),
        'miner': 'claymores-dual-ethereum-amd-gpu-98',
        'description': '',
    },
    {
        'name': 'Restart',
        'request': '{"id":0,"jsonrpc":"2.0","method":"miner_restart"}',
        'response': '',
        'miner': 'claymores-dual-ethereum-amd-gpu-98',
        'description': '',
    },
    {
        'name': 'Reboot',
        'request': '{"id":0,"jsonrpc":"2.0","method":"miner_reboot"}',
        'response': '',
        'miner': 'claymores-dual-ethereum-amd-gpu-98',
        'description': '',
    },
    {
        'name': 'GPU',
        'request': json.dumps(
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "control_gpu",
                "params": "{gpu}",
            },
        ),
        'response': '',
        'miner': 'claymores-dual-ethereum-amd-gpu-98',
        'description': '',
    },
    {
        'name': 'Statistic',
        'request': '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}',
        'response': json.dumps(
            {
                'Statistic': {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "error": {"type": "null"},
                        "result": {
                            "items": {"type": "string"},
                            "minItems": 9,
                            "maxItems": 9,
                        },
                    },
                },
            },
        ),
        'miner': 'claymores-cryptonote-gpu-97',
        'description': '',
    },
    {
        'name': 'Restart',
        'request': '{"id":0,"jsonrpc":"2.0","method":"miner_restart"}',
        'response': '',
        'miner': 'claymores-cryptonote-gpu-97',
        'description': '',
    },
    {
        'name': 'Reboot',
        'request': '{"id":0,"jsonrpc":"2.0","method":"miner_reboot"}',
        'response': '',
        'miner': 'claymores-cryptonote-gpu-97',
        'description': '',
    },
    {
        'name': 'GPU',
        'request': json.dumps(
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "control_gpu",
                "params": "{gpu}",
            },
        ),
        'response': '',
        'miner': 'claymores-cryptonote-gpu-97',
        'description': '',
    },
    {
        'name': 'Statistic',
        'request': b'{"id":0, "method":"getstat"}\n',
        'response': json.dumps(
            {
                'Statistic': {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "method": {"type": "string"},
                        "error": {"type": "null"},
                        "start_time": {"format": "utc-millisec"},
                        "current_server": {"type": "string"},
                        "available_servers": {"type": "integer"},
                        "server_status": {"type": "integer"},
                        "result": {
                            "items": {
                                "type": "object",
                                "properties": {
                                    "gpuid": {"type": "integer"},
                                    "cudaid": {"type": "integer"},
                                    "busid": {"type": "string"},
                                    "name": {"type": "string"},
                                    "gpu_status": {"type": "integer"},
                                    "solver": {"type": "integer"},
                                    "temperature": {"type": "integer"},
                                    "gpu_power_usage": {"type": "integer"},
                                    "speed_sps": {"type": "integer"},
                                    "accepted_shares": {"type": "integer"},
                                    "rejected_shares": {"type": "integer"},
                                    "start_time": {"format": "utc-millisec"},
                                },
                            },
                            "minItems": 1,
                        },
                    },
                },
            }

        ),
        'miner': 'ewbfs-cuda-zcash-034b',
        'description': '',
    },
    {
        'name': 'Summary',
        'request': '{"command": "summary"}',
        'response': json.dumps(
            {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "enum": ["w", "i", "s", "e", "f"]
                                    },
                                    "when": {"format": "utc-millisec"},
                                    "code": {"type": "integer"},
                                    "msg": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                            },
                        ],
                        "minitems": 1,
                        "maxitems": 1,
                    },
                    "id": {"type": "integer"},
                    "SUMMARY": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "Elapsed": {"type": "integer"},
                                    "GHS 5s": {"type": "string"},
                                    "GHS av": {"type": "number"},
                                    "Found Blocks": {"type": "integer"},
                                    "Getworks": {"type": "integer"},
                                    "Accepted": {"type": "integer"},
                                    "Rejected": {"type": "integer"},
                                    "Hardware Errors": {"type": "integer"},
                                    "Utility": {"type": "number"},
                                    "Discarded": {"type": "integer"},
                                    "Stale": {"type": "integer"},
                                    "Get Failures": {"type": "integer"},
                                    "Local Work": {"type": "integer"},
                                    "Remote Failures": {"type": "integer"},
                                    "Network Blocks": {"type": "integer"},
                                    "Total MH": {"type": "number"},
                                    "Work Utility": {"type": "number"},
                                    "Difficulty Accepted": {"type": "number"},
                                    "Difficulty Rejected": {"type": "number"},
                                    "Difficulty Stale": {"type": "number"},
                                    "Best Share": {"type": "integer"},
                                    "Device Hardware%": {"type": "number"},
                                    "Device Rejected%": {"type": "number"},
                                    "Pool Rejected%": {"type": "number"},
                                    "Pool Stale%": {"type": "number"},
                                    "Last getwork": {"format": "utc-millisec"},
                                },
                            },
                        ],
                        "minItems": 1,
                        "maxItems": 1,
                    },
                },
            }
        ),
        'miner': 'antminer-s9-cgminer-490',
        'description': '',
    },
    {
        'name': 'Stats',
        'request': '{"command": "stats"}',
        'response': json.dumps(
            {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "enum": ["w", "i", "s", "e", "f"]
                                    },
                                    "when": {"format": "utc-millisec"},
                                    "code": {"type": "integer"},
                                    "msg": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                            },
                        ],
                        "minitems": 1,
                        "maxitems": 1,
                    },
                    "id": {"type": "integer"},
                    "STATS": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "BMMiner": {"type": "string"},
                                    "Miner": {"type": "string"},
                                    "CompileTime": {"type": "string"},
                                    "Type": {"type": "string"},
                                    "STATS": {"type": "integer"},
                                    "ID": {"type": "string"},
                                    "Elapsed": {"type": "integer"},
                                    "Calls": {"type": "integer"},
                                    "Wait": {"type": "number"},
                                    "Max": {"type": "number"},
                                    "Min": {"type": "number"},
                                    "GHS 5s": {"type": "string"},
                                    "GHS av": {"type": "number"},
                                    "miner_count": {"type": "integer"},
                                    "frequency": {"type": "string"},
                                    "fan_num": {"type": "integer"},
                                    "temp_num": {"type": "integer"},
                                    "total_rateideal": {"type": "number"},
                                    "total_freqavg": {"type": "number"},
                                    "total_acn": {"type": "integer"},
                                    "total_rate": {"type": "number"},
                                    "temp_max": {"type": "integer"},
                                    "Device Hardware%": {"type": "number"},
                                    "no_matching_work": {"type": "integer"},
                                    "miner_version": {"type": "string"},
                                    "miner_id": {"type": "string"},
                                },
                                "patternProperties": {
                                    "^temp[0-9]+": {"type": "integer"},
                                    "^temp[0-9]+_[0-9]+": {"type": "integer"},
                                    "^freq_avg[0-9]+": {"type": "number"},
                                    "^chain_rateideal[0-9]+": {"type": "number"},
                                    "^chain_acn[0-9]+": {"type": "integer"},
                                    "^chain_acs[0-9]+": {
                                        "type": "string",
                                        "blank": True,
                                    },
                                    "^chain_hw[0-9]+": {"type": "integer"},
                                    "^chain_rate[0-9]+": {
                                        "type": "string",
                                        "blank": True,
                                    },
                                    "^chain_xtime[0-9]+": {
                                        "type": "string",
                                        "blank": True,
                                    },
                                    "^chain_offside_[0-9]+": {
                                        "type": "string",
                                        "blank": True,
                                    },
                                    "^chain_opencore_[0-9]+": {
                                        "type": "string",
                                        "blank": True,
                                    },
                                },
                            },
                        ],
                        "minItems": 1,
                        "maxItems": 1,
                    },
                },
            }
        ),
        'miner': 'antminer-s9-cgminer-490',
        'description': '',
    }
]

def add_request_data(apps, schema_editor):
    Request = apps.get_model('miner', 'Request')
    Miner = apps.get_model('miner', 'Miner')
    for request in REQUESTS:
        new_request = Request.objects.create(
            name=request['name'],
            request=request['request'],
            response=request['response'],
            miner=Miner.objects.get(slug=request['miner']),
            description=request['description'],
        )
        new_request.slug = get_unique_slug(
            new_request,
            'slug',
            'name',
            unique=('miner', )
        )
        new_request.save()

def remove_request_data(apps, schema_editor):
    Request = apps.get_model('miner', 'Request')
    Miner = apps.get_model('miner', 'Miner')
    for request in REQUESTS:
        request_object = Request.objects.get(
            name=request['name'],
            miner=Miner.objects.get(slug=request['miner']),
        )
        request_object.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('miner', '0003_server_data'),
    ]

    operations = [
        migrations.RunPython(
            add_request_data,
            remove_request_data)
    ]
