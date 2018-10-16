import os

from ..log_filters import ManagementFilter

from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'localhost',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware',)

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Logging

verbose = (
    "[%(asctime)s] %(log_color)s%(levelname)s%(reset)s"
    " [%(name)s:%(lineno)s] %(funcName)s [%(cyan)s%(message)s%(reset)s]"
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'remove_migration_sql': {
            '()': ManagementFilter,
        },
    },
    'formatters': {
        'verbose': {
            'format': verbose,
            'datefmt': "%Y-%b-%d %H:%M:%S",
            '()': 'colorlog.ColoredFormatter',
            'log_colors': {
                'DEBUG': 'bold_blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
    },
    'handlers': {
        'console': {
            'filters': [
                'remove_migration_sql',
            ],
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': [
                'console',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
        'debug': {
            'handlers': [
                'console',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
            'propagate': False,
        }
    },
}
